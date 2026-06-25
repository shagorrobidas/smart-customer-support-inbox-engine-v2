import re


class AISuggetionsService:
    RULES = [
        (
            r"(refund|money back|cancel|reimburse)",
            "We are sorry to hear that you want a refund. Our policy allows refunds within 30 days of purchase for unused items. Please provide your order ID so we can process this for you."
        ),
        (
            r"(broken|damaged|faulty|not working|defect)",
            "We apologize that your product arrived damaged or faulty. Please send us a photo of the item, and we will happily arrange a free replacement or a full refund immediately."
        ),
        (
            r"(late|delay|shipping|where is my order|tracking|delivery)",
            "Thank you for reaching out about your delivery. Let me check the shipping status for you. Could you please provide your tracking number or order ID?"
        ),
        (
            r"(price|cost|expensive|discount|promo|coupon)",
            "Thanks for asking about our pricing! We occasionally offer promotional discounts. You can use the coupon code 'WELCOME10' for a 10% discount on your next order."
        ),
        (
            r"(hello|hi|hey|greetings|anyone there)",
            "Hello! Thank you for contacting our support team. How can I assist you today?"
        )
    ]

    @classmethod
    def suggest_reply(cls, message_text: str) -> str:
        if not message_text:
            return "Thank you for reaching out. How can we help you today?"

        msg_lower = message_text.lower()
        for pattern, suggestion in cls.RULES:
            if re.search(pattern, msg_lower):
                return suggestion

        return "Thank you for your message. A support agent has been notified and will review your request shortly to assist you."
