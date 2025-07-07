import { useState, useRef, useEffect } from 'react'
import {
  Box,
  Button,
  Input,
  Text,
  VStack,
  HStack,
  Flex,
  Spinner,
  useToast,
  Badge,
  Wrap,
  WrapItem,
  useColorModeValue,
  IconButton,
  Divider
} from '@chakra-ui/react'
import { ChatIcon, ArrowForwardIcon } from '@chakra-ui/icons'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5001'

const ChatInterface = ({ uploadedFiles, systemStatus }) => {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [suggestedQuestions] = useState([
    "How many vacation days do I get as a new employee?",
    "What's the process for requesting sick leave?",
    "Can I work remotely and what are the guidelines?",
    "How do I enroll in health insurance?",
    "What are the company holidays?",
    "How do I request time off?",
    "What's the dress code policy?",
    "How does the 401k plan work?"
  ])
  
  const messagesEndRef = useRef(null)
  const toast = useToast()

  const messageBg = useColorModeValue('white', 'gray.700')
  const userMessageBg = useColorModeValue('primary.500', 'primary.600')
  const assistantMessageBg = useColorModeValue('gray.100', 'gray.600')
  const borderColor = useColorModeValue('gray.200', 'gray.600')

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Welcome message
    if (messages.length === 0) {
      setMessages([{
        id: 1,
        text: "Hello! I'm your HR Assistant. I can help you find information about company policies, benefits, leave procedures, and more. What would you like to know?",
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        sources: []
      }])
    }
  }, [])

  const handleSendMessage = async (messageText = inputValue) => {
    if (!messageText.trim()) return

    const userMessage = {
      id: Date.now(),
      text: messageText,
      sender: 'user',
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        query: messageText
      })

      const assistantMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        sources: response.data.sources || [],
        confidence: response.data.confidence
      }

      setMessages(prev => [...prev, assistantMessage])

    } catch (error) {
      console.error('Chat error:', error)
      
      let errorMessage = "I'm having trouble processing your request. Please try again."
      
      if (error.response?.status === 500) {
        errorMessage = "There seems to be a server issue. Please check if LM Studio is running."
      } else if (error.code === 'ECONNREFUSED') {
        errorMessage = "Cannot connect to the server. Please make sure the backend is running on port 5001."
      }

      const errorAssistantMessage = {
        id: Date.now() + 1,
        text: errorMessage,
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        sources: [],
        isError: true
      }

      setMessages(prev => [...prev, errorAssistantMessage])
      
      toast({
        title: 'Error',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleSuggestedQuestion = (question) => {
    handleSendMessage(question)
  }

  const formatTimestamp = (isoString) => {
    const date = new Date(isoString)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const getConfidenceColor = (confidence) => {
    switch (confidence) {
      case 'high': return 'green'
      case 'medium': return 'yellow'
      case 'low': return 'orange'
      default: return 'gray'
    }
  }

  const isLMStudioConnected = systemStatus?.services?.llm_service !== false

  return (
    <VStack spacing={4} align="stretch" h="600px">
      {/* Header */}
      <Box textAlign="center" pb={2}>
        <Text fontSize="2xl" fontWeight="bold" mb={2}>
          HR Assistant Chat
        </Text>
        <HStack justifyContent="center" spacing={4}>
          <Badge colorScheme="blue">
            {uploadedFiles.length} Document{uploadedFiles.length !== 1 ? 's' : ''} Loaded
          </Badge>
          {!isLMStudioConnected && (
            <Badge colorScheme="red">
              AI Service Offline
            </Badge>
          )}
        </HStack>
      </Box>

      {/* Messages Area */}
      <Box
        flex="1"
        overflowY="auto"
        border="1px solid"
        borderColor={borderColor}
        borderRadius="md"
        p={4}
        bg={messageBg}
      >
        <VStack spacing={4} align="stretch">
          {messages.map((message) => (
            <Box key={message.id}>
              <Flex
                justify={message.sender === 'user' ? 'flex-end' : 'flex-start'}
                align="flex-start"
              >
                <Box
                  maxW="70%"
                  bg={message.sender === 'user' ? userMessageBg : assistantMessageBg}
                  color={message.sender === 'user' ? 'white' : 'inherit'}
                  p={3}
                  borderRadius="lg"
                  boxShadow="sm"
                >
                  <Text>{message.text}</Text>
                  
                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <Box mt={2}>
                      <Text fontSize="xs" opacity={0.8} mb={1}>
                        Sources:
                      </Text>
                      <VStack spacing={1} align="stretch">
                        {message.sources.map((source, index) => (
                          <Box
                            key={index}
                            bg="blackAlpha.200"
                            p={2}
                            borderRadius="sm"
                            fontSize="xs"
                          >
                            <Text fontWeight="semibold">{source.document}</Text>
                            <Text>Relevance: {(source.relevance_score * 100).toFixed(0)}%</Text>
                          </Box>
                        ))}
                      </VStack>
                    </Box>
                  )}
                  
                  {/* Confidence Badge */}
                  {message.confidence && (
                    <HStack mt={2} spacing={2}>
                      <Badge
                        size="sm"
                        colorScheme={getConfidenceColor(message.confidence)}
                      >
                        {message.confidence} confidence
                      </Badge>
                    </HStack>
                  )}
                </Box>
              </Flex>
              
              <Text
                fontSize="xs"
                color="gray.500"
                textAlign={message.sender === 'user' ? 'right' : 'left'}
                mt={1}
              >
                {formatTimestamp(message.timestamp)}
              </Text>
            </Box>
          ))}
          
          {isLoading && (
            <Flex justify="flex-start">
              <HStack
                bg={assistantMessageBg}
                p={3}
                borderRadius="lg"
                boxShadow="sm"
              >
                <Spinner size="sm" />
                <Text>Thinking...</Text>
              </HStack>
            </Flex>
          )}
          
          <div ref={messagesEndRef} />
        </VStack>
      </Box>

      {/* Suggested Questions */}
      {messages.length <= 1 && (
        <Box>
          <Text fontSize="sm" color="gray.600" mb={2}>
            Try asking:
          </Text>
          <Wrap spacing={2}>
            {suggestedQuestions.slice(0, 6).map((question, index) => (
              <WrapItem key={index}>
                <Button
                  size="sm"
                  variant="outline"
                  colorScheme="primary"
                  onClick={() => handleSuggestedQuestion(question)}
                  isDisabled={isLoading || !isLMStudioConnected}
                >
                  {question}
                </Button>
              </WrapItem>
            ))}
          </Wrap>
        </Box>
      )}

      {/* Input Area */}
      <HStack spacing={2}>
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={
            !isLMStudioConnected 
              ? "AI service is offline. Please start LM Studio." 
              : "Type your HR question here..."
          }
          isDisabled={isLoading || !isLMStudioConnected}
          bg={useColorModeValue('white', 'gray.700')}
        />
        <IconButton
          icon={<ArrowForwardIcon />}
          onClick={() => handleSendMessage()}
          isDisabled={isLoading || !inputValue.trim() || !isLMStudioConnected}
          colorScheme="primary"
          aria-label="Send message"
        />
      </HStack>
      
      {!isLMStudioConnected && (
        <Box
          bg={useColorModeValue('orange.50', 'orange.900')}
          p={3}
          borderRadius="md"
          border="1px solid"
          borderColor={useColorModeValue('orange.200', 'orange.600')}
        >
          <Text fontSize="sm" color="orange.800">
            <strong>LM Studio Not Connected:</strong> Please make sure LM Studio is running on localhost:1234 with the Mistral-7B model loaded.
          </Text>
        </Box>
      )}
    </VStack>
  )
}

export default ChatInterface 