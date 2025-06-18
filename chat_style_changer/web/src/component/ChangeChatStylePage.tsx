import { AUTH_HEADER, BASE_URL } from '@/config/Cofig';
import { Box, Button, Sheet, Stack, Textarea, Typography } from '@mui/joy';
import axios from "axios";
import { useState } from "react";

export default function ChangeChatStylePage() {
    const [context, setContext] = useState('');
    const [sentence, setSentence] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState('');
    const [responseJson, setResponseJson] = useState<any>(null);
  
    const handleConvert = async () => {
      if (!sentence.trim()) {
        // window.alert('변환할 문장을 입력해주세요.');
        return;
      }
      setIsLoading(true);
      setResponseJson(null);
      try {
        const response = await axios.post(`${BASE_URL}/api/v1/convert`, {
          query: sentence,
          context_messages: context,
        }, { headers: AUTH_HEADER });
        setResult(response.data.converted || '변환 완료');
        setResponseJson(response.data);
        // window.alert('문장이 성공적으로 변환되었습니다.');
      } catch (error: any) {
        setResult('');
        setResponseJson(error?.response?.data || error?.toString());
        // window.alert('변환 중 오류가 발생했습니다.');
      } finally {
        setIsLoading(false);
      }
    };
  
    return (
      <Box p={4}>
        <Stack>
          <Typography level="h2" mb={2}>
            Chat Style Changer
          </Typography>
          <Box mb={2}>
            <Typography level="h4" mb={2}>
              Formatted Context Messages (Copy/Paste)
            </Typography>
            <Textarea
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="Copy and paste former context messages here..."
              minRows={20}
            />
          </Box>
          <Box mb={2}>
            <Typography level="h4" mb={2}>
              Target Query
            </Typography>
            <Textarea
              value={sentence}
              onChange={(e) => setSentence(e.target.value)}
              placeholder="Input target query here..."
              minRows={1}
            />
          </Box>
          <Button
            color="neutral"
            size="lg"
            onClick={handleConvert}
            loading={isLoading}
          >
            convert
          </Button>
          {responseJson && (
            <Box sx={{ mt: 2 }}>
              <Typography level="body-md">전체 응답(JSON):</Typography>
              <Sheet variant="soft" sx={{ p: 2, borderRadius: 'md', bgcolor: 'neutral.900', color: 'common.white', fontFamily: 'monospace', whiteSpace: 'pre', overflowX: 'auto' }}>
                {JSON.stringify(responseJson, null, 2)}
              </Sheet>
            </Box>
          )}
        </Stack>
      </Box>
    );
  }