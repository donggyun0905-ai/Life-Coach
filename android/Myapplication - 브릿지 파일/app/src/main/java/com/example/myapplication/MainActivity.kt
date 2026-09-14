package com.example.myapplication

import android.content.Context
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.PermissionController
import androidx.health.connect.client.records.*
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import androidx.lifecycle.lifecycleScope
import androidx.work.*
import com.google.gson.annotations.SerializedName
import kotlinx.coroutines.launch
import retrofit2.*
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.POST
import java.time.Instant
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.util.concurrent.TimeUnit

// ✅ 메인 액티비티
class MainActivity : AppCompatActivity() {
    private lateinit var healthConnectClient: HealthConnectClient
    private val permissions = setOf(
        HealthPermission.getReadPermission(StepsRecord::class),
        HealthPermission.getReadPermission(HeartRateRecord::class),
        HealthPermission.getReadPermission(DistanceRecord::class),
        HealthPermission.getReadPermission(ActiveCaloriesBurnedRecord::class),
        HealthPermission.getReadPermission(SleepSessionRecord::class),
        HealthPermission.getReadPermission(ExerciseSessionRecord::class),
        HealthPermission.getReadPermission(OxygenSaturationRecord::class)
    )

    private val requestPermissionLauncher = registerForActivityResult(
        PermissionController.createRequestPermissionResultContract()
    ) { grantedPermissions ->
        if (grantedPermissions.containsAll(permissions)) {
            Log.d("Permission", "✅ 모든 권한 허용됨")
        } else {
            Log.e("Permission", "❌ 필요한 권한이 거부됨")
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        healthConnectClient = HealthConnectClient.getOrCreate(this)

        // 권한 요청 버튼
        findViewById<Button>(R.id.btn_request_permission).setOnClickListener {
            lifecycleScope.launch {
                val granted = healthConnectClient.permissionController.getGrantedPermissions()
                if (!granted.containsAll(permissions)) {
                    requestPermissionLauncher.launch(permissions)
                } else {
                    Log.d("Permission", "✅ 권한 이미 있음")
                    Toast.makeText(this@MainActivity, "권한이 이미 허용되어 있습니다", Toast.LENGTH_SHORT).show()
                }
            }
        }

        // 테스트용: 15분 주기를 기다리지 않고 즉시 한 번 동기화
        findViewById<Button>(R.id.btn_sync_now).setOnClickListener {
            Toast.makeText(this, "동기화 시작...", Toast.LENGTH_SHORT).show()
            val syncNowRequest = OneTimeWorkRequestBuilder<HealthWorker>().build()
            WorkManager.getInstance(this).enqueue(syncNowRequest)
            WorkManager.getInstance(this).getWorkInfoByIdLiveData(syncNowRequest.id)
                .observe(this) { info ->
                    if (info != null && info.state.isFinished) {
                        val msg = if (info.state == androidx.work.WorkInfo.State.SUCCEEDED) "동기화 완료" else "동기화 실패 (Logcat 확인)"
                        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
                    }
                }
        }

        // ✅ WorkManager: 15분마다 실행
        val workRequest = PeriodicWorkRequestBuilder<HealthWorker>(15, TimeUnit.MINUTES).build()
        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "health_worker",
            ExistingPeriodicWorkPolicy.UPDATE,
            workRequest
        )
    }
}

// ✅ 이 기기가 보내는 모든 건강 데이터에 붙는 uid.
// 백엔드가 데이터를 uid별로 구분해서 저장/조회하므로, 프론트에서 이 uid로
// 사용자를 등록해야 이 기기가 보낸 데이터가 화면에 보인다.
const val DEVICE_UID = "phone_test_001"

// ✅ WorkManager
class HealthWorker(appContext: Context, workerParams: WorkerParameters) :
    CoroutineWorker(appContext, workerParams) {

    private val healthConnectClient = HealthConnectClient.getOrCreate(appContext)
    private val permissions = setOf(
        HealthPermission.getReadPermission(StepsRecord::class),
        HealthPermission.getReadPermission(HeartRateRecord::class),
        HealthPermission.getReadPermission(DistanceRecord::class),
        HealthPermission.getReadPermission(ActiveCaloriesBurnedRecord::class),
        HealthPermission.getReadPermission(SleepSessionRecord::class),
        HealthPermission.getReadPermission(ExerciseSessionRecord::class),
        HealthPermission.getReadPermission(OxygenSaturationRecord::class)
    )

    override suspend fun doWork(): Result {
        return try {
            Log.d("HealthWorker", "⏰ WorkManager 실행됨 (15분 주기)")

            val granted = healthConnectClient.permissionController.getGrantedPermissions()
            if (!granted.containsAll(permissions)) {
                Log.e("HealthWorker", "❌ 권한 없음")
                return Result.failure()
            }

            val end = LocalDateTime.now()
            val start15m = end.minusMinutes(15)
            val start1d = end.minusDays(1)

            readAndSendSteps(start15m, end)
            readAndSendHeartRate(start15m, end)
            readAndSendDistance(start15m, end)
            readAndSendCalories(start15m, end)
            readAndSendSleep(start1d, end)
            readAndSendExercise(start1d, end)
            readAndSendOxygen(start1d, end)

            Result.success()
        } catch (e: Exception) {
            Log.e("HealthWorker", "❌ 오류: ${e.message}")
            Result.retry()
        }
    }

    // ✅ 공통: LocalDateTime → Instant 변환 (Duration 계산용)
    private fun toInstant(time: LocalDateTime): Instant =
        time.toInstant(ZoneOffset.UTC)

    // ✅ 걸음
    private suspend fun readAndSendSteps(start: LocalDateTime, end: LocalDateTime) {
        val response = healthConnectClient.readRecords(
            ReadRecordsRequest(StepsRecord::class, TimeRangeFilter.between(start, end))
        )
        Log.d("HealthWorker", "📊 걸음 ${response.records.size}건 ($start ~ $end)")
        response.records.forEach {
            val minutesAgo = java.time.Duration.between(it.endTime, end).toMinutes()
            Log.d("HealthWorker", "걸음 ${it.count} | 종료=${it.endTime} | ${minutesAgo}분 전")
        }
        val data = response.records.map { StepData(DEVICE_UID, it.count, it.startTime.toString(), it.endTime.toString()) }
        HealthSender.sendSteps(data)
    }

    // ✅ 심박수
    private suspend fun readAndSendHeartRate(start: LocalDateTime, end: LocalDateTime) {
        val response = healthConnectClient.readRecords(
            ReadRecordsRequest(HeartRateRecord::class, TimeRangeFilter.between(start, end))
        )
        Log.d("HealthWorker", "❤️ 심박 ${response.records.size}건")
        val data = response.records.flatMap { record ->
            record.samples.map {
                val minutesAgo = java.time.Duration.between(it.time, toInstant(end)).toMinutes()
                Log.d("HealthWorker", "심박 ${it.beatsPerMinute}bpm | ${minutesAgo}분 전")
                HeartRateData(DEVICE_UID, it.beatsPerMinute.toDouble(), it.time.toString())
            }
        }
        HealthSender.sendHeartRate(data)
    }

    // ✅ 거리
    private suspend fun readAndSendDistance(start: LocalDateTime, end: LocalDateTime) {
        val response = healthConnectClient.readRecords(
            ReadRecordsRequest(DistanceRecord::class, TimeRangeFilter.between(start, end))
        )
        Log.d("HealthWorker", "📏 거리 ${response.records.size}건")
        val data = response.records.map {
            DistanceData(DEVICE_UID, it.distance.inMeters, it.startTime.toString(), it.endTime.toString())
        }
        HealthSender.sendDistance(data)
    }

    // ✅ 칼로리
    private suspend fun readAndSendCalories(start: LocalDateTime, end: LocalDateTime) {
        val response = healthConnectClient.readRecords(
            ReadRecordsRequest(ActiveCaloriesBurnedRecord::class, TimeRangeFilter.between(start, end))
        )
        Log.d("HealthWorker", "🔥 칼로리 ${response.records.size}건")
        val data = response.records.map {
            CalorieData(DEVICE_UID, it.energy.inKilocalories, it.startTime.toString(), it.endTime.toString())
        }
        HealthSender.sendCalories(data)
    }

    // ✅ 수면
    private suspend fun readAndSendSleep(start: LocalDateTime, end: LocalDateTime) {
        val response = healthConnectClient.readRecords(
            ReadRecordsRequest(SleepSessionRecord::class, TimeRangeFilter.between(start, end))
        )
        Log.d("HealthWorker", "😴 수면 ${response.records.size}건")
        val data = response.records.map {
            SleepData(DEVICE_UID, it.title ?: "Sleep Session", it.startTime.toString(), it.endTime.toString())
        }
        HealthSender.sendSleep(data)
    }

    // ✅ 운동
    private suspend fun readAndSendExercise(start: LocalDateTime, end: LocalDateTime) {
        val response = healthConnectClient.readRecords(
            ReadRecordsRequest(ExerciseSessionRecord::class, TimeRangeFilter.between(start, end))
        )
        Log.d("HealthWorker", "🏃 운동 ${response.records.size}건")
        val data = response.records.map {
            ExerciseData(DEVICE_UID, it.title, it.startTime.toString(), it.endTime.toString(), it.exerciseType.toString())
        }
        HealthSender.sendExercise(data)
    }

    // ✅ 산소포화도
    private suspend fun readAndSendOxygen(start: LocalDateTime, end: LocalDateTime) {
        val response = healthConnectClient.readRecords(
            ReadRecordsRequest(OxygenSaturationRecord::class, TimeRangeFilter.between(start, end))
        )
        Log.d("HealthWorker", "🫁 산소포화도 ${response.records.size}건")
        val data = response.records.map {
            OxygenData(DEVICE_UID, it.percentage.value, it.time.toString())
        }
        HealthSender.sendOxygen(data)
    }
}

// ✅ 서버 전송 모듈
object HealthSender {
    // ⚠️ 테스트용: PC에서 로컬로 띄운 백엔드 (같은 Wi-Fi에 있어야 함)
    // Render 서버가 복구되면 "https://capstone-lozi.onrender.com" 로 되돌리기
    private const val BASE_URL = "http://192.168.75.224:8000"
    private const val TOKEN = "capstone_token_0905"

    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    private val service = retrofit.create(ApiService::class.java)

    fun sendSteps(data: List<StepData>) = service.sendSteps(data, "Bearer $TOKEN").enqueue(log("걸음"))
    fun sendHeartRate(data: List<HeartRateData>) = service.sendHeartRate(data, "Bearer $TOKEN").enqueue(log("심박수"))
    fun sendDistance(data: List<DistanceData>) = service.sendDistance(data, "Bearer $TOKEN").enqueue(log("거리"))
    fun sendCalories(data: List<CalorieData>) = service.sendCalories(data, "Bearer $TOKEN").enqueue(log("칼로리"))
    fun sendSleep(data: List<SleepData>) = service.sendSleep(data, "Bearer $TOKEN").enqueue(log("수면"))
    fun sendExercise(data: List<ExerciseData>) = service.sendExercise(data, "Bearer $TOKEN").enqueue(log("운동"))
    fun sendOxygen(data: List<OxygenData>) = service.sendOxygen(data, "Bearer $TOKEN").enqueue(log("산소포화도"))

    private fun <T> log(name: String) = object : Callback<T> {
        override fun onResponse(call: Call<T>, response: Response<T>) {
            Log.d("POST", "✅ $name 전송 성공: ${response.code()}")
        }
        override fun onFailure(call: Call<T>, t: Throwable) {
            Log.e("POST", "❌ $name 전송 실패: ${t.message}")
        }
    }
}

// ✅ DTO (백엔드가 각 항목마다 uid를 필수로 요구함)
data class StepData(val uid: String, val count: Long, @SerializedName("start_time") val startTime: String, @SerializedName("end_time") val endTime: String)
data class HeartRateData(val uid: String, val bpm: Double, val time: String)
data class DistanceData(val uid: String, @SerializedName("distance") val distanceMeters: Double, @SerializedName("start_time") val startTime: String, @SerializedName("end_time") val endTime: String)
data class CalorieData(val uid: String, @SerializedName("calories_kcal") val energyKcal: Double, @SerializedName("start_time") val startTime: String, @SerializedName("end_time") val endTime: String)
data class SleepData(val uid: String, val title: String?, @SerializedName("start_time") val startTime: String, @SerializedName("end_time") val endTime: String)
data class ExerciseData(val uid: String, val title: String?, @SerializedName("start_time") val startTime: String, @SerializedName("end_time") val endTime: String, @SerializedName("exercise_type") val exerciseType: String)
data class OxygenData(val uid: String, val percentage: Double, val time: String)

// ✅ Retrofit API
interface ApiService {
    @POST("/v1/ingest/steps") fun sendSteps(@Body data: List<StepData>, @Header("Authorization") token: String): Call<Void>
    @POST("/v1/ingest/heartrate") fun sendHeartRate(@Body data: List<HeartRateData>, @Header("Authorization") token: String): Call<Void>
    @POST("/v1/ingest/distance") fun sendDistance(@Body data: List<DistanceData>, @Header("Authorization") token: String): Call<Void>
    @POST("/v1/ingest/calories") fun sendCalories(@Body data: List<CalorieData>, @Header("Authorization") token: String): Call<Void>
    @POST("/v1/ingest/sleep") fun sendSleep(@Body data: List<SleepData>, @Header("Authorization") token: String): Call<Void>
    @POST("/v1/ingest/exercise") fun sendExercise(@Body data: List<ExerciseData>, @Header("Authorization") token: String): Call<Void>
    @POST("/v1/ingest/oxygen") fun sendOxygen(@Body data: List<OxygenData>, @Header("Authorization") token: String): Call<Void>
}
