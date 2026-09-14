import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

const STORAGE_KEY = 'lifecoach.session.v1';
const SessionContext = createContext(null);

function loadInitialState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    // localStorage 접근 불가(프라이빗 모드 등) 시 기본값으로 진행
  }
  return { guardians: [], users: [], selectedUser: null, isLoggedIn: false };
}

export function SessionProvider({ children }) {
  const [state, setState] = useState(loadInitialState);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      // 저장 실패는 무시 (세션 유지가 안 될 뿐 앱 동작에는 지장 없음)
    }
  }, [state]);

  const findByUid = useCallback(
    (uid) =>
      state.guardians.find((g) => g.uid === uid) ||
      state.users.find((u) => u.uid === uid) ||
      null,
    [state.guardians, state.users]
  );

  const registerGuardian = useCallback((uid) => {
    setState((s) => ({
      ...s,
      guardians: [...s.guardians, { uid, nickname: uid }],
      isLoggedIn: true,
    }));
  }, []);

  const registerUser = useCallback((uid) => {
    const newUser = { uid, nickname: uid };
    setState((s) => ({
      ...s,
      users: [...s.users, newUser],
      selectedUser: newUser,
      isLoggedIn: true,
    }));
    return newUser;
  }, []);

  const upsertUser = useCallback((uid, nickname) => {
    setState((s) => {
      const idx = s.users.findIndex((u) => u.uid === uid);
      const users =
        idx !== -1
          ? s.users.map((u, i) => (i === idx ? { ...u, nickname } : u))
          : [...s.users, { uid, nickname }];
      return { ...s, users };
    });
  }, []);

  const setSelectedUser = useCallback((user) => {
    setState((s) => ({ ...s, selectedUser: user }));
  }, []);

  const login = useCallback((asGuardian) => {
    setState((s) => ({ ...s, isLoggedIn: true, selectedUser: asGuardian ? null : s.selectedUser }));
  }, []);

  const logout = useCallback(() => {
    setState((s) => ({ ...s, isLoggedIn: false, selectedUser: null }));
  }, []);

  const value = useMemo(
    () => ({
      ...state,
      findByUid,
      registerGuardian,
      registerUser,
      upsertUser,
      setSelectedUser,
      login,
      logout,
    }),
    [state, findByUid, registerGuardian, registerUser, upsertUser, setSelectedUser, login, logout]
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession() {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error('useSession은 SessionProvider 내부에서만 사용할 수 있습니다.');
  return ctx;
}
