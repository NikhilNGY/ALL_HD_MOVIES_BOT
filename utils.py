import re
import logging
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI, DATABASE_NAME, COLLECTION_NAME

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
instance = Instance(db)


@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_ref = fields.StrField()
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField()
    mime_type = fields.StrField()
    caption = fields.StrField()
    
    class Meta:
        collection_name = COLLECTION_NAME
        
        
async def save_file(media):
    """Save file in database"""
    
    file = Media(
        file_id=media.file_id,
        file_ref=media.file_ref,
        file_name=media.file_name,
        file_size=media.file_size,
        file_type=media.file_type,
        mime_type=media.mime_type,
    )
    
    caption = media.caption
    if caption:
        file.caption = caption
    
    try:
        await file.commit()
    except DuplicateKeyError:
        logger.warning(media.file_name + " is already saved in database")
    else:
        logger.info(media.file_name + " is saved in database")
    

async def get_search_results(query, max_results=10):
    """For given query return results in async generator form"""

    raw_pattern = query.lower().strip().replace(' ', '.?')
    if not raw_pattern:
        raw_pattern = '.'
        
    try:
        regex = re.compile(raw_pattern, re.IGNORECASE)
    except:
        return []

    return await Media.find({'file_name':regex}).sort('$natural', -1).limit(max_results).to_list(length=max_results)