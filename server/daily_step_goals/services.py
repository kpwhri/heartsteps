class StepGoalsService:
    def __init__(self, user):
        assert user is not None, "User must be specified"
        
        self.user = user
    
    def get_step_goal(self, date=None):
        """returns step goal

        Args:
            date ([datetime], optional): date to fetch the step goal. Defaults to None. If omitted, today's goal is fetched

        Returns:
            [int]: step goal of the day
        """
        return 8001;