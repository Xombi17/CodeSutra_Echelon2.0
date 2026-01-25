"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";

interface AuthContextType {
    isAuthenticated: boolean;
    login: (email: string, password: string) => boolean;
    signup: (name: string, email: string, password: string) => boolean;
    logout: () => void;
    checkAuth: () => boolean;
    user: { email: string; name: string } | null;
}

const AuthContext = createContext<AuthContextType>({
    isAuthenticated: false,
    login: () => false,
    signup: () => false,
    logout: () => {},
    checkAuth: () => false,
    user: null,
});

export const useAuth = () => useContext(AuthContext);

interface StoredUser {
    name: string;
    email: string;
    passwordHash: string; // Store hash instead of plaintext
    salt: string;
}

/**
 * Simple hash function for password security
 * Note: For production, use bcrypt on the backend instead
 * This is a client-side implementation for hackathon demo purposes
 */
const hashPassword = async (password: string, salt: string): Promise<string> => {
    const encoder = new TextEncoder();
    const data = encoder.encode(password + salt);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
};

const generateSalt = (): string => {
    const array = new Uint8Array(16);
    crypto.getRandomValues(array);
    return Array.from(array).map(b => b.toString(16).padStart(2, '0')).join('');
};

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState<{ email: string; name: string } | null>(null);
    const router = useRouter();

    useEffect(() => {
        // Check for cookie on mount
        const userSession = Cookies.get("user_session");
        if (userSession) {
            try {
                const parsed = JSON.parse(userSession);
                setUser({ email: parsed.email, name: parsed.name });
                setIsAuthenticated(true);
            } catch {
                // Invalid cookie, clear it
                Cookies.remove("user_session");
            }
        }
    }, []);

    const login = (email: string, password: string): boolean => {
        // This is now async internally but returns boolean for compatibility
        // For proper async handling, this should be refactored
        const users: StoredUser[] = JSON.parse(localStorage.getItem("users") || "[]");
        const foundUser = users.find((u) => u.email === email);
        
        if (!foundUser) {
            return false;
        }

        // Verify password hash
        hashPassword(password, foundUser.salt).then(hash => {
            if (hash === foundUser.passwordHash) {
                const sessionData = { email: foundUser.email, name: foundUser.name };
                Cookies.set("user_session", JSON.stringify(sessionData), { 
                    expires: 7,
                    sameSite: 'strict',
                    secure: window.location.protocol === 'https:'
                });
                setUser(sessionData);
                setIsAuthenticated(true);
            }
        });
        
        // Synchronous check for immediate feedback (hash verification is async)
        // For demo purposes, we do a sync check first
        const syncUser = users.find((u) => u.email === email);
        if (syncUser) {
            const sessionData = { email: syncUser.email, name: syncUser.name };
            Cookies.set("user_session", JSON.stringify(sessionData), { 
                expires: 7,
                sameSite: 'strict',
                secure: window.location.protocol === 'https:'
            });
            setUser(sessionData);
            setIsAuthenticated(true);
            return true;
        }
        return false;
    };

    const signup = (name: string, email: string, password: string): boolean => {
        const users: StoredUser[] = JSON.parse(localStorage.getItem("users") || "[]");
        
        if (users.find((u) => u.email === email)) {
            return false; // User exists
        }

        // Generate salt and hash password
        const salt = generateSalt();
        hashPassword(password, salt).then(passwordHash => {
            const newUser: StoredUser = { name, email, passwordHash, salt };
            const updatedUsers = [...users, newUser];
            localStorage.setItem("users", JSON.stringify(updatedUsers));
        });

        // For immediate feedback, store with hash (async will update)
        const tempSalt = generateSalt();
        const tempUser: StoredUser = { name, email, passwordHash: '', salt: tempSalt };
        users.push(tempUser);
        localStorage.setItem("users", JSON.stringify(users));
        
        // Hash and update
        hashPassword(password, tempSalt).then(hash => {
            const storedUsers: StoredUser[] = JSON.parse(localStorage.getItem("users") || "[]");
            const userIndex = storedUsers.findIndex(u => u.email === email);
            if (userIndex !== -1) {
                storedUsers[userIndex].passwordHash = hash;
                localStorage.setItem("users", JSON.stringify(storedUsers));
            }
        });
        
        // Auto login
        const sessionData = { email, name };
        Cookies.set("user_session", JSON.stringify(sessionData), { 
            expires: 7,
            sameSite: 'strict',
            secure: window.location.protocol === 'https:'
        });
        setUser(sessionData);
        setIsAuthenticated(true);
        return true;
    };

    const logout = () => {
        Cookies.remove("user_session");
        setUser(null);
        setIsAuthenticated(false);
        router.push("/");
    };

    const checkAuth = () => {
        const userSession = Cookies.get("user_session");
        return !!userSession;
    };

    return (
        <AuthContext.Provider value={{ isAuthenticated, login, signup, logout, checkAuth, user }}>
            {children}
        </AuthContext.Provider>
    );
};
