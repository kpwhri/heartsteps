import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { FitbitModule } from '@heartsteps/fitbit/fitbit.module';
import { LocationModule } from '@heartsteps/locations/location.module';
import { NotificationsModule } from '@heartsteps/notifications/notifications.module';
import { ContactInformationModule } from '@heartsteps/contact-information/contact-information.module';
import { ActivitySuggestionsModule } from '@heartsteps/activity-suggestions/activity-suggestions.module';
import { PlacesModule } from '@heartsteps/places/places.module';
import { WeeklySurveyModule } from '@heartsteps/weekly-survey/weekly-survey.module';

import { ParticipantService } from './participant.service';
import { ProfileService } from './profile.factory';

@NgModule({
    imports: [
        InfrastructureModule,
        FitbitModule,
        LocationModule,
        NotificationsModule,
        ContactInformationModule,
        ActivitySuggestionsModule,
        PlacesModule,
        WeeklySurveyModule
    ],
    providers: [
        ParticipantService,
        ProfileService
    ]
})
export class ParticipantModule {}
