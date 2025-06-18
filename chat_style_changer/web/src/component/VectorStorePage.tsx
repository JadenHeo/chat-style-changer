import axios from "axios";
import { Box, Button, Sheet, Typography, Stack, Modal, ModalDialog, ModalClose, Input } from '@mui/joy';
import { useEffect, useState } from "react";
import { LuUpload } from "react-icons/lu";
import { AUTH_HEADER, BASE_URL } from "@/config/Cofig";
import { MdDelete, MdUpload } from "react-icons/md";

interface FileInfo {
  filename: string;
  size: number;
  created_at: string;
}

export default function VectorStorePage() {
  const [loading, setLoading] = useState(false);
  
  const [collections, setCollections] = useState<[string, number][]>([]);
  const [loadedCollection, setLoadedCollection] = useState<string | null>(null);
  const [newCollectionName, setNewCollectionName] = useState('');
  const [addCollectionModalOpen, setAddCollectionModalOpen] = useState(false);

  const [files, setFiles] = useState<FileInfo[]>([]);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [selectedFile, setSelectedFile] = useState<FileInfo | null>(null);
  const [fileViewModalOpen, setFileViewModalOpen] = useState(false);
  const [fileContent, setFileContent] = useState('');
  
  // Fetch collections and loaded collection on mount
  useEffect(() => {
    fetchCollections();
    fetchFiles();
  }, []);

  const fetchCollections = async () => {
    try {
      const [allRes, loadedRes] = await Promise.all([
        axios.get(`${BASE_URL}/api/v1/vector-store/collections`, { headers: AUTH_HEADER }),
        axios.get(`${BASE_URL}/api/v1/vector-store/collections:loaded`, { headers: AUTH_HEADER }),
      ]);
      setCollections(allRes.data.collections || []);
      setLoadedCollection(loadedRes.data.loaded_collection || null);
    } catch (e) {
      window.alert('컬렉션 정보를 불러오지 못했습니다.');
    }
  };

  // Load a collection
  const handleLoad = async (name: string) => {
    setLoading(true);
    try {
      await axios.post(`${BASE_URL}/api/v1/vector-store/collections:load`, null, { headers: AUTH_HEADER, params: { name } });
      setLoadedCollection(name);
      window.alert(`${name} 컬렉션 로드 완료`);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCollection = async (name: string) => {
    setLoading(true);
    try {
      await axios.post(`${BASE_URL}/api/v1/vector-store/collections`, null, { headers: AUTH_HEADER, params: { name } });
      setLoadedCollection(name);
    } catch(e) {
      window.alert('컬렉션 추가에 실패했습니다.');
    } finally {
      await fetchCollections();
      setLoading(false);
      setAddCollectionModalOpen(false);
    }
  };

  const handleDeleteCollection = async (name: string) => {
    setLoading(true);
    try {
      await axios.delete(`${BASE_URL}/api/v1/vector-store/collections`, { headers: AUTH_HEADER, params: { name } });
    } catch(e) {
      window.alert('컬렉션 제거에 실패했습니다.');
    } finally {
      await fetchCollections();
      setLoading(false);
    }
  };

  const fetchFiles = async () => {
    try {
      const response = await axios.get(`${BASE_URL}/api/v1/file-manager/files`, { headers: AUTH_HEADER });
      setFiles(response.data || []);
    } catch(e) {
      window.alert('파일 목록을 불러오지 못했습니다.');
    }
  };

  const handleUploadFile = async (file: File | null) => {
    if (!file) {
      window.alert('파일을 선택해주세요.');
      return;
    }
    try {
      const formData = new FormData();
      formData.append('file', file);
      await axios.post(`${BASE_URL}/api/v1/file-manager/files:upload`, formData, { headers: AUTH_HEADER });
    } catch(e) {
      window.alert('파일 업로드에 실패했습니다.');
    } finally {
      await fetchFiles();
    }
  };

  const handleDeleteFile = async (filename: string) => {
    setLoading(true);
    try {
      await axios.delete(`${BASE_URL}/api/v1/file-manager/files/${filename}`, { headers: AUTH_HEADER });
    } catch(e) {
      window.alert('파일 삭제에 실패했습니다.');
    } finally {
      await fetchFiles();
      setLoading(false);
    }
  }

  const handleViewFile = async (file: FileInfo) => {
    setLoading(true);
    try {
      setSelectedFile(file);
      const response = await axios.get(`${BASE_URL}/api/v1/file-manager/files/${file.filename}`, { headers: AUTH_HEADER });
      setFileContent(response.data);
      setFileViewModalOpen(true)
    } catch(e) {
      window.alert('파일 보기에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }

  const handleUploadVector = async (file: FileInfo) => {
    setLoading(true);
    try {
      const req = {
        file_name: file.filename,
        collection_name: loadedCollection,
        user_name: '허홍준'
      }

      let buffer = '';
      await axios.post(
        `${BASE_URL}/api/v1/vector-store/collections/vectors:upload`, 
        req, 
        { 
          headers: AUTH_HEADER,
          onDownloadProgress(event) {
            // event.currentTarget.response에 누적된 전체 텍스트가 들어있음
            buffer = event.event.data as string;
  
            // 빈 줄(\n\n) 단위로 청크 분리
            const parts = buffer.split(/\r?\n\r?\n/);
            buffer = parts.pop()!;  // 마지막 조각은 남겨두기
  
            for (const part of parts) {
              // 각 파트는 "data: {...}" 형태
              for (const line of part.split(/\r?\n/)) {
                if (line.startsWith('data:')) {
                  const json = line.slice(5).trim();
                  try {
                    const evt = JSON.parse(json);
                    console.log('SSE 이벤트:', evt);
                    // ▶️ 받은 이벤트로 UI 업데이트 or state 변경
                  } catch {
                    console.warn('파싱 실패:', json);
                  }
                }
              }
            }
          } 
        }
      );
    } catch(e) {
      window.alert('파일 마운트에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <Box p={4}>
      <Stack direction="row" spacing={6} alignItems="flex-start">
        <Stack spacing={2} flex={1}>
          <Typography level="h3" mb={2}>Manage Collections From Vector Store</Typography>
          <Stack spacing={1}>
            {collections.length === 0 && <Typography color="neutral">컬렉션이 없습니다.</Typography>}
            {collections.sort().map(([name, count]) => (
              <Stack 
                direction="row" 
                spacing={1} 
              >
                <Button
                  color={name === loadedCollection ? 'neutral' : 'neutral'}
                  variant={name === loadedCollection ? 'solid' : 'outlined'}
                  onClick={name === loadedCollection || loading ? undefined : () => handleLoad(name)}
                  size="lg"
                  sx={{ 
                    width: '100%',
                    justifyContent: 'flex-start',
                    cursor: name === loadedCollection || loading ? 'not-allowed' : 'pointer',
                    '&:hover': {
                      opacity: name === loadedCollection || loading ? 0.7 : 1,
                    },
                  }}
                >
                  {name} ({count} data)
                </Button>
                <Button
                  color="danger"
                  variant="outlined"
                  size="lg"
                  disabled={loading}
                  onClick={() => handleDeleteCollection(name)}
                >
                  <MdDelete />
                </Button>
              </Stack>
            ))}
            <Button
              variant="solid"
              color="primary"
              size="lg"
              onClick={() => setAddCollectionModalOpen(true)}
            >
              +
            </Button>
          </Stack>
        </Stack>
        <Stack spacing={2} flex={1}>
          <Typography level="h3" mb={2}>Upload New Chat Data</Typography>
          <Stack spacing={1}>
            {files.sort((a, b) => a.filename.localeCompare(b.filename)).map((file) => (
              <Stack 
              direction="row" 
              spacing={1} 
              >
                <Button 
                  color={file.filename === selectedFile?.filename ? 'neutral' : 'neutral'}
                  variant={file.filename === selectedFile?.filename ? 'solid' : 'outlined'}
                  size="lg"
                  sx={{ 
                    width: '100%',
                    justifyContent: 'flex-start',
                    '&:hover': {
                      opacity: file.filename === selectedFile?.filename || loading ? 0.7 : 1,
                    },
                  }}
                  onClick={file.filename === selectedFile?.filename ? undefined : () => handleViewFile(file)}
                >
                  {file.filename}
                </Button>
                <Button
                  color="danger"
                  variant="outlined"
                  size="lg"
                  disabled={loading}
                  onClick={() => handleDeleteFile(file.filename)}
                >
                  <MdDelete />
                </Button>
                <Button
                  color="primary"
                  variant="outlined"
                  size="lg"
                  disabled={loading}
                  onClick={() => handleUploadVector(file)}
                >
                  <MdUpload />
                </Button>
              </Stack>
            ))}
          </Stack>
          <Box>
            <Button
              variant="solid"
              color="primary"
              component="label"
            >
              <LuUpload /> Upload *.csv
              <input 
                type="file" 
                hidden 
                onChange={(e) => {
                  const files = e.target.files;
                  if (files && files.length > 0) {
                    handleUploadFile(files[0])
                  }
                }}
              />
            </Button>
          </Box>
        </Stack>
      </Stack>

      <Modal open={addCollectionModalOpen} onClose={() => setAddCollectionModalOpen(false)}>
        <ModalDialog>
          <ModalClose />
            <Typography level="h4" mb={2}>Add New Collection</Typography>
            <Stack spacing={2}>
              <Input
                placeholder="Enter collection name"
                value={newCollectionName}
                onChange={(e) => setNewCollectionName(e.target.value)}
                autoFocus
              />
              <Button onClick={() => handleAddCollection(newCollectionName)} loading={loading}>
                Add
              </Button>
            </Stack>
        </ModalDialog>
      </Modal>

      <Modal 
        open={fileViewModalOpen} 
        onClose={() => setFileViewModalOpen(false)}
      >
        <ModalDialog
          variant="outlined"
          sx={{
              maxWidth: '80vw',
              maxHeight: '80vh',
              width: '100%',
              overflow: 'auto',
          }}
        >
          <ModalClose />
          <Typography level="h4" mb={2}>
            {selectedFile?.filename}
          </Typography>
          <Sheet 
            variant="outlined" 
            sx={{ 
                p: 2, 
                borderRadius: 'sm',
                bgcolor: 'background.level1',
                fontFamily: 'monospace',
                whiteSpace: 'pre-wrap',
                overflow: 'auto',
                maxHeight: '60vh'
            }}
          >
            <Typography level="body-sm">
              {fileContent}
            </Typography>
          </Sheet>
        </ModalDialog>
      </Modal>
    </Box>
  );
}