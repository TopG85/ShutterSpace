from django import template
from cloudinary import CloudinaryImage

register = template.Library()


@register.simple_tag
def optimized_image_url(cloudinary_field, transform_type='thumbnail'):
    """
    Generate optimized Cloudinary URLs for different contexts.
    Args:
        cloudinary_field: Cloudinary field from model
        transform_type: Type of transformation (thumbnail, detail, hero)
    Returns:
        Optimized image URL string
    """
    if not cloudinary_field:
        return ''
    # Extract public_id from the field
    public_id = str(cloudinary_field)
    # Define optimized transformations for different contexts
    transformations = {
        'thumbnail': {
            'width': 400,
            'height': 300,
            'crop': 'fill',
            'quality': 'auto:eco',
            'format': 'auto',
            'fetch_format': 'auto',
            'progressive': True,
            'secure': True
        },
        'detail': {
            'width': 800,
            'height': 600,
            'crop': 'limit',
            'quality': 'auto:good',
            'format': 'auto',
            'fetch_format': 'auto',
            'progressive': True,
            'secure': True
        },
        'hero': {
            'width': 1200,
            'height': 400,
            'crop': 'fill',
            'quality': 'auto:eco',
            'format': 'auto',
            'fetch_format': 'auto',
            'progressive': True,
            'secure': True
        },
        'avatar': {
            'width': 150,
            'height': 150,
            'crop': 'thumb',
            'gravity': 'face',
            'quality': 'auto:eco',
            'format': 'auto',
            'fetch_format': 'auto',
            'progressive': True,
            'secure': True
        }
    }
    # Get the transformation settings
    transform = transformations.get(
        transform_type, transformations['thumbnail']
    )
    # Create CloudinaryImage and apply transformations
    try:
        image = CloudinaryImage(public_id)
        return image.build_url(**transform)
    except Exception:
        # Fallback to original URL if transformation fails
        if hasattr(cloudinary_field, 'url'):
            return cloudinary_field.url
        return ''


@register.simple_tag
def responsive_image_srcset(cloudinary_field):
    """
    Generate responsive srcset for different screen sizes.
    Args:
        cloudinary_field: Cloudinary field from model
    Returns:
        srcset attribute string for responsive images
    """
    if not cloudinary_field:
        return ''
    public_id = str(cloudinary_field)
    # Define different sizes for responsive images
    sizes = [
        {'width': 400, 'descriptor': '400w'},
        {'width': 800, 'descriptor': '800w'},
        {'width': 1200, 'descriptor': '1200w'},
        {'width': 1600, 'descriptor': '1600w'},
    ]
    srcset_urls = []
    try:
        image = CloudinaryImage(public_id)
        for size in sizes:
            url = image.build_url(
                width=size['width'],
                crop='limit',
                quality='auto:eco',
                format='auto',
                fetch_format='auto',
                progressive=True,
                secure=True
            )
            srcset_urls.append(f"{url} {size['descriptor']}")
        return ', '.join(srcset_urls)
    except Exception:
        return ''


@register.simple_tag
def lazy_image_attrs():
    """
    Return attributes for lazy loading images.
    Returns:
        String of HTML attributes for lazy loading
    """
    return 'loading="lazy" decoding="async"'
