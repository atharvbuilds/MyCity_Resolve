from django.utils.text import slugify
import re

def extract_hashtags(text):
    """Extract hashtags from text content"""
    pattern = r'#(\w+)'
    return set(re.findall(pattern, text))

def process_hashtags(text, issue):
    """Process hashtags in text and associate them with an issue"""
    from .models import Hashtag
    
    hashtags = extract_hashtags(text)
    for tag_name in hashtags:
        tag, created = Hashtag.objects.get_or_create(name=slugify(tag_name))
        if created or issue not in tag.issues.all():
            tag.usage_count += 1
            tag.save()
        issue.hashtags.add(tag)
    return text

def format_hashtags(text):
    """Convert hashtags in text to links"""
    pattern = r'#(\w+)'
    return re.sub(pattern, r'<a href="/hashtag/\1" class="hashtag">#\1</a>', text)