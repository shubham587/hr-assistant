import { useState, useEffect } from 'react'
import {
  Box,
  Container,
  Heading,
  VStack,
  HStack,
  Button,
  useToast,
  Flex,
  Text,
  Badge,
  useColorModeValue
} from '@chakra-ui/react'
import { AttachmentIcon, ChatIcon } from '@chakra-ui/icons'
import FileUpload from './components/FileUpload'
import ChatInterface from './components/ChatInterface'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5001'

function App() {
  const [activeTab, setActiveTab] = useState('upload')
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [systemStatus, setSystemStatus] = useState(null)
  const toast = useToast()

  const bgColor = useColorModeValue('gray.50', 'gray.900')
  const cardBg = useColorModeValue('white', 'gray.800')

  // Check system health on component mount
  useEffect(() => {
    checkSystemHealth()
  }, [])

  const checkSystemHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`)
      setSystemStatus(response.data)
    } catch (error) {
      console.error('System health check failed:', error)
      setSystemStatus({ status: 'unhealthy' })
    }
  }

  const handleFileUpload = async (file) => {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setUploadedFiles(prev => [...prev, {
        name: file.name,
        size: file.size,
        uploadTime: new Date().toISOString()
      }])

      toast({
        title: 'Success!',
        description: `${file.name} has been uploaded and processed.`,
        status: 'success',
        duration: 5000,
        isClosable: true
      })

      // Switch to chat tab after successful upload
      setActiveTab('chat')

    } catch (error) {
      console.error('Upload failed:', error)
      toast({
        title: 'Upload failed',
        description: error.response?.data?.error || 'Failed to upload file',
        status: 'error',
        duration: 5000,
        isClosable: true
      })
    }
  }

  const getStatusColor = (status) => {
    if (status === 'healthy') return 'green'
    if (status === 'unhealthy') return 'red'
    return 'yellow'
  }

  return (
    <Box minH="100vh" bg={bgColor}>
      <Container maxW="container.xl" py={8}>
        <VStack spacing={8}>
          {/* Header */}
          <Box textAlign="center">
            <Heading as="h1" size="2xl" mb={4} color="primary.600">
              HR Assistant
            </Heading>
            <Text fontSize="lg" color="gray.600">
              Your AI-powered HR knowledge companion
            </Text>
            
            {/* System Status */}
            {systemStatus && (
              <HStack justifyContent="center" mt={4}>
                <Badge colorScheme={getStatusColor(systemStatus.status)}>
                  System {systemStatus.status}
                </Badge>
                {systemStatus.services?.llm_service === false && (
                  <Badge colorScheme="orange">
                    LM Studio Disconnected
                  </Badge>
                )}
              </HStack>
            )}
          </Box>

          {/* Navigation */}
          <HStack spacing={4}>
            <Button
              leftIcon={<AttachmentIcon />}
              onClick={() => setActiveTab('upload')}
              variant={activeTab === 'upload' ? 'solid' : 'outline'}
              colorScheme="primary"
            >
              Upload Documents
            </Button>
            <Button
              leftIcon={<ChatIcon />}
              onClick={() => setActiveTab('chat')}
              variant={activeTab === 'chat' ? 'solid' : 'outline'}
              colorScheme="primary"
              isDisabled={uploadedFiles.length === 0}
            >
              Chat Assistant
            </Button>
          </HStack>

          {/* Main Content */}
          <Box
            w="full"
            bg={cardBg}
            borderRadius="lg"
            boxShadow="lg"
            p={6}
            minH="500px"
          >
            {activeTab === 'upload' ? (
              <FileUpload
                onFileUpload={handleFileUpload}
                uploadedFiles={uploadedFiles}
              />
            ) : (
              <ChatInterface
                uploadedFiles={uploadedFiles}
                systemStatus={systemStatus}
              />
            )}
          </Box>

          {/* Footer */}
          <Box textAlign="center" mt={8}>
            <Text fontSize="sm" color="gray.500">
              Upload your HR documents and ask questions about policies, benefits, and procedures.
            </Text>
          </Box>
        </VStack>
      </Container>
    </Box>
  )
}

export default App 