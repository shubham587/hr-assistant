import { useState } from 'react'
import {
  Box,
  Button,
  Text,
  VStack,
  HStack,
  Progress,
  List,
  ListItem,
  ListIcon,
  useToast,
  Flex,
  Icon,
  useColorModeValue
} from '@chakra-ui/react'
import { useDropzone } from 'react-dropzone'
import { AttachmentIcon, CheckCircleIcon, WarningIcon } from '@chakra-ui/icons'

const FileUpload = ({ onFileUpload, uploadedFiles }) => {
  const [isUploading, setIsUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const toast = useToast()

  const borderColor = useColorModeValue('gray.300', 'gray.600')
  const hoverBorderColor = useColorModeValue('primary.500', 'primary.400')
  const bgColor = useColorModeValue('gray.50', 'gray.700')
  const activeBgColor = useColorModeValue('primary.50', 'primary.900')

  const onDrop = async (acceptedFiles) => {
    const file = acceptedFiles[0]
    
    if (!file) {
      toast({
        title: 'No file selected',
        description: 'Please select a PDF file to upload.',
        status: 'warning',
        duration: 3000,
        isClosable: true
      })
      return
    }

    if (file.type !== 'application/pdf') {
      toast({
        title: 'Invalid file type',
        description: 'Please select a PDF file.',
        status: 'error',
        duration: 3000,
        isClosable: true
      })
      return
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      toast({
        title: 'File too large',
        description: 'Please select a file smaller than 10MB.',
        status: 'error',
        duration: 3000,
        isClosable: true
      })
      return
    }

    setIsUploading(true)
    try {
      await onFileUpload(file)
    } catch (error) {
      // Error handling is done in parent component
    } finally {
      setIsUploading(false)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false,
    disabled: isUploading
  })

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatUploadTime = (isoString) => {
    const date = new Date(isoString)
    return date.toLocaleString()
  }

  return (
    <VStack spacing={6} align="stretch">
      <Box textAlign="center">
        <Text fontSize="2xl" fontWeight="bold" mb={2}>
          Upload HR Documents
        </Text>
        <Text color="gray.600">
          Upload PDF documents containing HR policies, employee handbooks, or benefits information
        </Text>
      </Box>

      {/* Drag and Drop Area */}
      <Box
        {...getRootProps()}
        border="2px dashed"
        borderColor={isDragActive ? hoverBorderColor : borderColor}
        borderRadius="lg"
        p={8}
        textAlign="center"
        cursor="pointer"
        bg={isDragActive ? activeBgColor : bgColor}
        transition="all 0.2s"
        _hover={{
          borderColor: hoverBorderColor,
          bg: activeBgColor
        }}
      >
        <input {...getInputProps()} />
        <VStack spacing={4}>
          <Icon as={AttachmentIcon} w={12} h={12} color="primary.500" />
          {isDragActive ? (
            <Text fontSize="lg" color="primary.600">
              Drop the PDF file here...
            </Text>
          ) : (
            <VStack spacing={2}>
              <Text fontSize="lg" fontWeight="semibold">
                Drag & drop a PDF file here
              </Text>
              <Text color="gray.500">or</Text>
              <Button
                colorScheme="primary"
                variant="outline"
                size="md"
                isDisabled={isUploading}
              >
                Choose File
              </Button>
            </VStack>
          )}
          <Text fontSize="sm" color="gray.500">
            Supported format: PDF (max 10MB)
          </Text>
        </VStack>
      </Box>

      {/* Upload Progress */}
      {isUploading && (
        <Box>
          <Text mb={2} fontSize="sm" color="gray.600">
            Processing document...
          </Text>
          <Progress isIndeterminate colorScheme="primary" />
        </Box>
      )}

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <Box>
          <Text fontSize="lg" fontWeight="semibold" mb={4}>
            Uploaded Documents ({uploadedFiles.length})
          </Text>
          <List spacing={3}>
            {uploadedFiles.map((file, index) => (
              <ListItem key={index}>
                <Flex
                  align="center"
                  justify="space-between"
                  p={3}
                  bg={useColorModeValue('green.50', 'green.900')}
                  borderRadius="md"
                  border="1px solid"
                  borderColor={useColorModeValue('green.200', 'green.600')}
                >
                  <HStack>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    <VStack align="start" spacing={1}>
                      <Text fontWeight="medium">{file.name}</Text>
                      <HStack spacing={4}>
                        <Text fontSize="sm" color="gray.600">
                          {formatFileSize(file.size)}
                        </Text>
                        <Text fontSize="sm" color="gray.600">
                          {formatUploadTime(file.uploadTime)}
                        </Text>
                      </HStack>
                    </VStack>
                  </HStack>
                </Flex>
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {/* Instructions */}
      <Box bg={useColorModeValue('blue.50', 'blue.900')} p={4} borderRadius="md">
        <Text fontSize="sm" color="blue.800">
          <strong>Tips:</strong>
          <br />
          • Upload employee handbooks, policy documents, or benefits guides
          <br />
          • Ensure documents contain clear text (not scanned images)
          <br />
          • Documents will be processed and made searchable for the AI assistant
          <br />
          • You can upload multiple documents to build a comprehensive knowledge base
        </Text>
      </Box>
    </VStack>
  )
}

export default FileUpload 