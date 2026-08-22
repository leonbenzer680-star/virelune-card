"""Claude AI Connector - Direct API Integration"""

import os
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class ClaudeConnector:
    """Connect to Claude API and get AI responses"""

    def __init__(self):
        """Initialize Claude client"""
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY not set in .env")

        self.client = Anthropic()
        self.model = "claude-3-5-sonnet-20241022"
        self.conversation_history = []
        logger.info("Claude connector initialized")

    def ask(self, question: str, context: dict = None) -> dict:
        """
        Ask Claude a question with optional context

        Args:
            question: The question to ask
            context: Optional context (emails, calendar events, etc.)

        Returns:
            Response with answer and metadata
        """
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(context)

            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": question})

            logger.info(f"Asking Claude: {question}")

            # Call Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=self.conversation_history,
            )

            # Extract answer
            answer = response.content[0].text

            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": answer})

            # Keep history limited to last 20 messages
            if len(self.conversation_history) > 40:
                self.conversation_history = self.conversation_history[-40:]

            logger.info("Claude responded successfully")

            return {
                "status": "success",
                "question": question,
                "answer": answer,
                "model": self.model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
            }

        except Exception as e:
            logger.error(f"Error calling Claude: {e}")
            return {
                "status": "error",
                "question": question,
                "error": str(e),
                "answer": "Sorry, I couldn't process that request. Please try again.",
            }

    def _build_system_prompt(self, context: dict = None) -> str:
        """Build system prompt with context"""
        base_prompt = """You are a personal AI assistant running on the user's laptop.

Your role:
- Answer questions helpfully and concisely
- Access the user's Gmail, Calendar, Drive, etc (when connected)
- Help find information quickly
- Remember context from previous messages
- Be honest about what you can and cannot do

When answering:
- Be direct and concise
- Provide specific information when available
- Ask clarifying questions if needed
- Suggest next steps if relevant

Current time: Use current time context if available.
Connected services: Gmail, Calendar, Drive, Contacts (status shown below)
"""

        if context:
            context_str = "\n\nCurrent Context:\n"
            if "services" in context:
                context_str += f"Connected Services: {', '.join(context['services'])}\n"
            if "user_info" in context:
                context_str += f"User: {context['user_info']}\n"
            base_prompt += context_str

        return base_prompt

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")

    def summarize_emails(self, emails: list) -> str:
        """Summarize a list of emails using Claude"""
        if not emails:
            return "No emails to summarize"

        email_text = "Here are your recent emails:\n\n"
        for email in emails:
            email_text += f"From: {email.get('from', 'Unknown')}\n"
            email_text += f"Subject: {email.get('subject', 'No subject')}\n"
            email_text += f"Preview: {email.get('preview', 'No preview')}\n\n"

        response = self.ask(
            f"Summarize these emails and highlight what's important:\n\n{email_text}"
        )
        return response.get("answer", "Could not summarize emails")

    def check_health(self) -> bool:
        """Check if Claude API is accessible"""
        try:
            response = self.client.messages.create(
                model=self.model, max_tokens=10, messages=[{"role": "user", "content": "hi"}]
            )
            logger.info("Claude health check: OK")
            return True
        except Exception as e:
            logger.error(f"Claude health check failed: {e}")
            return False
