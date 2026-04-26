from django.contrib import admin

from .models import Alert, DecisionReview, DecisionRule, NotificationRoute, QualityScore


admin.site.register(DecisionRule)
admin.site.register(QualityScore)
admin.site.register(NotificationRoute)
admin.site.register(Alert)
admin.site.register(DecisionReview)
