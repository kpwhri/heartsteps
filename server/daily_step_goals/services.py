class StepGoalsService:
    def __init__(self, user):
        assert user is not None, "User must be specified"
        
        self.user = user
    
    def get_today_step_goal(self):
        return 8001;