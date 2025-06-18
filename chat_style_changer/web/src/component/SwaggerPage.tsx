import SwaggerUI from 'swagger-ui-react';
import 'swagger-ui-react/swagger-ui.css';
import { BASE_URL, AUTH_HEADER } from '@/config/Cofig';

export default function SwaggerPage() {
  return (
    <SwaggerUI
        // 스웨거 스펙이 있는 엔드포인트
        url={`${BASE_URL}/api/v1/openapi.json`}
        // 요청 전 헤더에 Authorization 토큰 주입
        requestInterceptor={(req) => {
            // AUTH_HEADER 객체의 모든 키·값을 헤더에 주입
            Object.entries(AUTH_HEADER).forEach(([key, value]) => {
                req.headers[key] = value;
            });
            return req;
          }}
        // 필요에 따라 기본 옵션 커스터마이즈 가능
        docExpansion="list"
        deepLinking={true}
    />
  );
}