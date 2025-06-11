import axios from "axios";
import { Box, Button, Sheet, Typography, Stack } from '@mui/joy';
import { useEffect, useState } from "react";
import { LuUpload } from "react-icons/lu";

export default function VectorStorePage() {
    const [collections, setCollections] = useState<string[]>([]);
    const [loaded, setLoaded] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
  
    // Fetch collections and loaded collection on mount
    useEffect(() => {
      fetchCollections();
    }, []);
  
    const fetchCollections = async () => {
      try {
        const [allRes, loadedRes] = await Promise.all([
          axios.get('http://localhost:8000/api/v1/vector-store/collections'),
          axios.get('http://localhost:8000/api/v1/vector-store/collections:loaded'),
        ]);
        setCollections(allRes.data.collections || []);
        setLoaded(loadedRes.data.loaded_collection || null);
        // window.alert('컬렉션 불러오기 완료.');
      } catch (e) {
        // window.alert('컬렉션 정보를 불러오지 못했습니다.');
      }
    };
  
    // Load a collection
    const handleLoad = async (name: string) => {
      setLoading(true);
      try {
        const promise = axios.post('http://localhost:8000/api/v1/vector-store/collections:load', null, { params: { name } });
        setLoaded(name);
        // window.alert(`${name} 컬렉션 로드 완료`);
      } finally {
        setLoading(false);
      }
    };
  
    return (
      <Box p={4}>
        <Stack direction="row" spacing={6} alignItems="flex-start">
          <Stack spacing={2} flex={1}>
            <Typography level="h3" mb={2}>Manage Collections From Vector Store</Typography>
            <Stack spacing={1}>
                {collections.length === 0 && <Typography color="neutral">컬렉션이 없습니다.</Typography>}
                {collections.map((name) => (
                  <Button
                    key={name}
                    color={name === loaded ? 'neutral' : 'neutral'}
                    variant={name === loaded ? 'solid' : 'outlined'}
                    onClick={name === loaded || loading ? undefined : () => handleLoad(name)}
                    size="lg"
                    sx={{ 
                      justifyContent: 'flex-start',
                      cursor: name === loaded || loading ? 'not-allowed' : 'pointer',
                      '&:hover': {
                        opacity: name === loaded || loading ? 0.7 : 1,
                      },
                    }}
                  >
                    {name}
                    {name === loaded && <Box component="span" fontWeight="bold">(active)</Box>}
                  </Button>
                ))}
            </Stack>
          </Stack>
          <Stack spacing={2} flex={1}>
            <Typography level="h3" mb={2}>Upload New Chat Data</Typography>
            <Sheet variant="outlined" sx={{ p: 4, minHeight: 200, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                <Box sx={{ fontSize: 40, color: 'neutral.500' }}><LuUpload /></Box>
                <Typography level="body-md">Drag and drop files here</Typography>
                <Typography level="body-sm" color="neutral">.csv</Typography>
            </Sheet>
          </Stack>
        </Stack>
      </Box>
    );
  }