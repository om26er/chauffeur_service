from chauffeur.models import ChauffeurBaseUser


class UserHelpers:
    def __init__(self, **kwargs):
        self.user = ChauffeurBaseUser.objects.get(**kwargs)

    def append_hire_count(self):
        self.user.number_of_hires += 1
        self.user.save()

    def get_push_key(self):
        return self.user.push_notification_key
