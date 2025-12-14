import pytest
from unittest.mock import Mock, patch
from app.services.llm_service import LLMService


@pytest.mark.asyncio
async def test_generate_response_success():
    """Test successful LLM response generation"""
    llm_service = LLMService()
    
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Hello! How can I help?"))]
    mock_response.usage = Mock(total_tokens=25)
    
    with patch.object(llm_service.client.chat.completions, 'create', return_value=mock_response):
        result = await llm_service.generate_response(
            [{"role": "user", "content": "Hi"}]
        )
    
    assert result["content"] == "Hello! How can I help?"
    assert result["tokens"] == 25


@pytest.mark.asyncio
async def test_generate_response_with_system_message():
    """Test that system message is added to conversation"""
    llm_service = LLMService()
    
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Response"))]
    mock_response.usage = Mock(total_tokens=10)
    
    with patch.object(llm_service.client.chat.completions, 'create', return_value=mock_response) as mock_create:
        await llm_service.generate_response(
            [{"role": "user", "content": "Test"}]
        )
        
        call_args = mock_create.call_args
        messages = call_args.kwargs['messages']
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"


@pytest.mark.asyncio
async def test_generate_response_api_error():
    """Test error handling when API fails"""
    llm_service = LLMService()
    
    with patch.object(llm_service.client.chat.completions, 'create', side_effect=Exception("API Error")):
        with pytest.raises(Exception, match="Failed to generate response"):
            await llm_service.generate_response(
                [{"role": "user", "content": "Hi"}]
            )