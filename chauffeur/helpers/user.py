from chauffeur.models import ChauffeurUser, PushIDs


class UserHelpers:
    def __init__(self, **kwargs):
        self.user = ChauffeurUser.objects.get(**kwargs)

    def append_hire_count(self):
        self.user.number_of_hires += 1
        self.user.save()

    def get_push_keys(self):
        push_ids = PushIDs(user=self.user)
        return [key for key in push_ids.push_key]
