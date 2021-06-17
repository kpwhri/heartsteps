from django.db import models

from django.contrib.auth.models import User
from participants.models import Study, Cohort, Participant

class StudyType(models.Model):
    HOURLY = "hourly"
    
    name = models.CharField(max_length=255, unique=True)
    admins = models.ManyToManyField(User, blank=False)
    active = models.BooleanField(default=True)
    frequency = models.CharField(max_length=20, default=HOURLY)
    
    def __str__(self):
        return "{} ({})".format(self.name, self.frequency)

class CohortAssignment(models.Model):
    cohort = models.OneToOneField(Cohort, on_delete=models.CASCADE)
    studytype = models.ForeignKey(StudyType, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return "{} - {}".format(self.cohort.name, self.studytype.name)

class PreloadedLevelSequenceFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    whenUploaded = models.DateTimeField(auto_now_add=True)
    nickname = models.CharField(max_length=255, unique=True)
    numberOfDays = models.IntegerField(null=False)
    numberOfSequences = models.IntegerField(null=False)
    
    def insert(user, filename, nickname, csv_lines):
        sequence_file = PreloadedLevelSequenceFile.objects.create(
            user=user,
            filename=filename,
            nickname=nickname,
            numberOfDays=0,
            numberOfSequences=0
        )
        
        line_index = 0
        for a_line in csv_lines:
            sequence_line = PreloadedLevelSequenceLine.objects.create(
                sequence_file=sequence_file,
                sequence_serial_number=line_index
            )
            
            level_sequence = a_line.split(",")
            
            day_index = 0
            bulk_levels = []
            for a_level in level_sequence:
                bulk_levels.append(PreloadedLevelSequenceLevel(
                    sequence_line = sequence_line,
                    day_serial_number = day_index,
                    level = a_level))
                day_index += 1
            PreloadedLevelSequenceLevel.objects.bulk_create(bulk_levels)
            line_index += 1
        
        sequence_file.numberOfDays = day_index
        sequence_file.numberOfSequences = line_index
        sequence_file.save()
        
        return sequence_file
    
    def __str__(self):
        return "PreloadedLevelSequenceFile(user={}, filename={}, nickname={}, numberOfDays={}, numberOfSequence={}, whenUploaded={})".format(self.user, self.filename, self.nickname, self.numberOfDays, self.numberOfSequences, self.whenUploaded)

class PreloadedLevelSequenceLine(models.Model):
    sequence_file = models.ForeignKey(PreloadedLevelSequenceFile, on_delete = models.CASCADE)
    sequence_serial_number = models.IntegerField(null=False)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['sequence_file', 'sequence_serial_number']

class PreloadedLevelSequenceLevel(models.Model):
    sequence_line = models.ForeignKey(PreloadedLevelSequenceLine, on_delete = models.CASCADE)
    day_serial_number = models.IntegerField(null=False)
    level = models.IntegerField(null=False)

class LevelLineAssignment(models.Model):
    study_type = models.ForeignKey(StudyType, null=False, on_delete = models.CASCADE)
    participant = models.ForeignKey(Participant, null=False, on_delete = models.CASCADE)
    preloaded_sequence_line = models.ForeignKey(PreloadedLevelSequenceLine, null=True, on_delete=models.CASCADE)
    when_assigned = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return 'study_type: {}, participant: {}, preloaded_line: {}, when: {}'.format(self.study_type, self.participant, self.preloaded_sequence_line, self.when_assigned)
    
class LevelAssignment(models.Model):
    line_assignment = models.ForeignKey(LevelLineAssignment, on_delete = models.CASCADE, null=False)
    participant = models.ForeignKey(Participant, null=False, on_delete = models.CASCADE)
    date = models.DateField(null=False)
    level = models.IntegerField(null=False)
    
    def __str__(self):
        return 'line_assignment: {}, participant: {}, date: {}, level: {}'.format(self.line_assignment, self.participant, self.date, self.level)

class Conditionality(models.Model):
    """Base Class for all conditionalities"""
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=1024)
    studytype = models.ForeignKey(StudyType, on_delete=models.CASCADE)
    module_path = models.CharField(max_length=1024, unique=True)
    """each module has only one conditionality object"""
    active = models.BooleanField(default=True)
    """means whether the conditionality is running or not. This can be reset to True anytime."""
    class Meta:
        unique_together = ['module_path', 'studytype']

class LogContents(models.Model):
    logtime = models.DateTimeField(auto_now_add=True)
    subject_str = models.CharField(max_length=255, null=True)
    object_str = models.CharField(max_length=255, null=True)
    purpose_str = models.CharField(max_length=255, null=True)
    value = models.TextField(null=True, blank=True)
    
    def if_this_else_that(x, this, that):
        if x:
            return this
        else:
            return that
    
    def __str__(self):
        return "{}: {} - {} [{}] | {}".format(self.logtime, self.purpose_str, self.subject_str, self.object_str, self.value)
    
    class Meta:
        indexes = [
            models.Index(fields=['-logtime']),
            models.Index(fields=['-logtime', 'subject_str']),
            models.Index(fields=['subject_str', 'object_str', 'purpose_str']),  # also covers s+o, s
            models.Index(fields=['subject_str', 'purpose_str']),            
            models.Index(fields=['purpose_str', 'object_str']),             # also covers p
            models.Index(fields=['object_str'])
        ] 

class ConditionalityParameter(models.Model):
    conditionality = models.ForeignKey(Conditionality, null=True, on_delete=models.SET_NULL)
    participant = models.ForeignKey(Participant, null=True, on_delete=models.SET_NULL)
    parameter_fullname = models.CharField(max_length=1024)
    period_begin = models.DateTimeField(auto_now_add=True)
    period_finish = models.DateTimeField(null=True)
    value = models.CharField(max_length=255)
    value_type = models.CharField(max_length=255)
    
    class Meta:
        unique_together = ['conditionality', 'participant', 'parameter_fullname', 'period_begin', 'period_finish']
        

    
class Preference(models.Model):
    participant = models.ForeignKey(Participant, null=True, on_delete=models.CASCADE)
    path = models.CharField(max_length=512)
    value = models.CharField(max_length=50)
    when_created = models.DateTimeField(auto_now_add=True)
    
    def try_to_get(path, participant=None, default=None, convert_to_int=False):
        """try to get a preference object

        Args:
            path (str): preference path/name
            participant (Participant, optional): filter condition. Defaults to None.
            default (str, optional): default value. if specified, it will be returned in case the db doesn't have this preference. Defaults to None.

        Returns:
            value (str): preference value
            fromdb (bool): if the preference exists in db
        """
        
        return_value = default
        return_fromdb = False
        
        query = Preference.objects.filter(path=path, participant=participant)
        if query.exists():
            return_value = query.order_by("-when_created").first().value
            return_fromdb = True
        
        if return_value and convert_to_int:
            return_value = int(return_value)
        
        return return_value, return_fromdb
        
    def create(path, value, participant=None):
        """create preference object

        Args:
            path (str): preference path/name
            value (str): set value

        Returns:
            Preference: added preference object
            bool: if overwritten
        """
        overwrite = Preference.objects.filter(path=path, participant=participant).exists()
        
        return Preference.objects.create(path=path, value=value, participant=participant), overwrite
    
    def delete(path, participant=None):
        return Preference.objects.filter(path=path, participant=participant).delete()