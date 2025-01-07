class AddContentDate:
    """Data processor to add ContentDate"""
    def __init__(self, identify=None):
        """Initial setup"""
        self.identify = identify

    async def process(self, item, item_type, header, mapping={}, updates=False):
        """Process item"""
        if self.identify: item_type = self.identify(item)
        if item_type == 'repex':
            item["ContentDate"] = header["ContentDate"]
        yield item

class RemoveEmptyExtension:
    """Data processor to remove empty Extension"""
    def __init__(self, identify=None):
        """Initial setup"""
        self.identify = identify

    async def process(self, item, item_type, header, mapping={}, updates=False):
        """Process item"""
        if self.identify: item_type = self.identify(item)
        if item_type == 'repex':
            if "Extension" in item and not isinstance(item["Extension"], dict):
                del item["Extension"]
        yield item
