export const BASE_URL = "https://heohongjun-chat-style-changer.hf.space";
// export const BASE_URL = "http://localhost:7860";

const token = import.meta.env.VITE_AUTH_TOKEN;
if (!token) {
  throw new Error("환경변수 VITE_AUTH_TOKEN이 설정되지 않았습니다!");
}

export const AUTH_HEADER = {
  Authorization: `Bearer ${token}`,
};