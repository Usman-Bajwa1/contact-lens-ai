from google import genai 
from google.genai import types
from app.core.config import GoogleSettings
from app.schema.app_schemas import ContactCreate, DuplicateCheckResult
from app.utils.prompts import GET_IMAGE_INFO, IMPROVE_DATA_PROMPT, DEDUPLICATION_PROMPT
import json

class Googlellm:
    def __init__(self):
        self.cfg = GoogleSettings()
        self._client = genai.Client(api_key=self.cfg.GOOGLE_API_KEY)
        
    async def get_contact_info(self, image_bytes: bytes) -> ContactCreate:
        response = await self._client.aio.models.generate_content(
            model=self.cfg.GOOGLE_MODEL_PRO,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                GET_IMAGE_INFO
            ],
            config={
                "response_mime_type": "application/json",
                "response_json_schema": ContactCreate.model_json_schema()
            }
        )
        return response.parsed

    async def improve_contact_data(self, current_data: dict) -> ContactCreate:
        prompt_with_data = IMPROVE_DATA_PROMPT.format(json_data=json.dumps(current_data))
        response = await self._client.aio.models.generate_content(
            model=self.cfg.GOOGLE_MODEL_PRO,
            contents=[prompt_with_data],
            config={
                "response_mime_type": "application/json",
                "response_json_schema": ContactCreate.model_json_schema()
            }
        )
        return response.parsed

    async def check_duplicate_semantic(self, new_data: dict, existing_list: list) -> DuplicateCheckResult:
        """Sends candidate + list to LLM for intelligent comparison"""
        if not existing_list:
            return DuplicateCheckResult(is_duplicate=False, reason="List is empty")

        simplified_list = [
            {"id": c["id"], "name": c["full_name"], "email": c.get("email"), "company": c.get("company")} 
            for c in existing_list
        ]

        prompt = DEDUPLICATION_PROMPT.format(
            existing_data=json.dumps(simplified_list),
            new_data=json.dumps(new_data)
        )

        response = await self._client.aio.models.generate_content(
            model=self.cfg.GOOGLE_MODEL_PRO,
            contents=[prompt],
            config={
                "response_mime_type": "application/json",
                "response_json_schema": DuplicateCheckResult.model_json_schema()
            }
        )
        return response.parsed



if __name__=="__main__":
    import asyncio

    async def main():
        llm = Googlellm()
        with open('2b33b670-e2c1-49dd-967d-1ba3f7427ec8.jpg', 'rb') as f:
            image_bytes = f.read()
        result = await llm.get_contact_info(image_bytes=image_bytes)
        print(result)

    asyncio.run(main())
        


