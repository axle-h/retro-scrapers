__author__ = 'Alex Haslehurst'


class RetroImage:
    def __init__(self, description, url, width, height, thumb_url):
        self.thumb_url = thumb_url
        self.height = height
        self.width = width
        self.url = url
        self.description = description

    def __str__(self, *args, **kwargs):
        return "%s, %s (%sx%s), %s" % (
            self.description, self.url, self.width, self.height, self.thumb_url)


class RetroSystem:
    def __init__(self, platform_name, platform, path, extensions):
        self.platform_name = platform_name
        self.platform = platform
        self.extensions = extensions
        self.path = path


class Rom:
    def __init__(self, source, file_name, title, description, boxart_front, boxart_back, release_date, publisher, developer,
                 genre, rating, players):
        self.file_name = file_name
        self.source = source
        self.title = title
        self.description = description
        self.boxart_front = boxart_front
        self.boxart_back = boxart_back
        self.release_date = release_date
        self.publisher = publisher
        self.developer = developer
        self.genre = genre
        self.rating = rating
        self.players = players
        self.image = ""

    def __str__(self, *args, **kwargs):
        return "%s, %s, %s, %s, %s, %s, %s\n%s\n%s\n%s" % (
            self.title, self.release_date, self.publisher, self.developer, self.genre, self.rating, self.players,
            self.boxart_front, self.boxart_back, self.description)