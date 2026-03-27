import React,{createContext,useContext,useState,useEffect} from 'react';
import {useRouter} from 'next/router';
interface AuthContextType{user:{id:number;role:string;token:string}|null;login:(t:string,r:string,id:number)=>void;logout:()=>void;isAdmin:boolean;isManager:boolean;isEmployee:boolean;}
const AuthContext=createContext<AuthContextType>({} as AuthContextType);
export function AuthProvider({children}:{children:React.ReactNode}){
  const[user,setUser]=useState<AuthContextType['user']>(null);
  const router=useRouter();
  useEffect(()=>{if(typeof window!=='undefined'){const t=localStorage.getItem('token'),r=localStorage.getItem('role'),id=localStorage.getItem('userId');if(t&&r&&id)setUser({token:t,role:r,id:parseInt(id)});}},[]);
  const login=(token:string,role:string,userId:number)=>{localStorage.setItem('token',token);localStorage.setItem('role',role);localStorage.setItem('userId',String(userId));setUser({token,role,id:userId});if(role==='admin'||role==='manager')router.push('/admin/dashboard');else router.push('/employee/dashboard');};
  const logout=()=>{localStorage.clear();setUser(null);router.push('/login');};
  return <AuthContext.Provider value={{user,login,logout,isAdmin:user?.role==='admin',isManager:user?.role==='manager',isEmployee:user?.role==='employee'}}>{children}</AuthContext.Provider>;
}
export const useAuth=()=>useContext(AuthContext);