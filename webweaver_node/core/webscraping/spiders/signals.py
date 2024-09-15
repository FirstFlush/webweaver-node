# from tortoise import signals
# from webweaver_node.webscraping.registry.scraping_registry import scraping_registry



# async def update_record_count(sender, instance, created, using_db, update_fields):
#     if created:
#         scraping_registry.increase_record(module_name=sender.__name__)


# signals.post_save().connect(update_record_count, sender=)
# # signals.post_save.connect(update_record_count, sender=MyScraperModel)