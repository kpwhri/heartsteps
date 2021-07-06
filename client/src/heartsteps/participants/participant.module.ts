import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { FitbitModule } from '@heartsteps/fitbit/fitbit.module';
import { NotificationsModule } from '@heartsteps/notifications/notifications.module';
import { ContactInformationModule } from '@heartsteps/contact-information/contact-information.module';
import { WalkingSuggestionsModule } from '@heartsteps/walking-suggestions/walking-suggestions.module';
import { PlacesModule } from '@heartsteps/places/places.module';
import { WeeklySurveyModule } from '@heartsteps/weekly-survey/weekly-survey.module';

import { ParticipantService } from './participant.service';
import { ProfileService } from './profile.factory';
import { DailyTimesModule } from '@heartsteps/daily-times/daily-times.module';
import { FitbitWatchModule } from '@heartsteps/fitbit-watch/fitbit-watch.module';
import { ParticipantInformationService } from './participant-information.service';
import { WeatherModule } from '@heartsteps/weather/weather.module';
import { BoutPlanningModule } from '@heartsteps/bout-planning/bout-planning.module';

@NgModule({
    imports: [
        DailyTimesModule,
        InfrastructureModule,
        FitbitModule,
        FitbitWatchModule,
        NotificationsModule,
        ContactInformationModule,
        WalkingSuggestionsModule,
        PlacesModule,
        WeeklySurveyModule,
        WeatherModule,
        BoutPlanningModule
    ],
    providers: [
        ParticipantService,
        ProfileService,
        ParticipantInformationService
    ]
})
export class ParticipantModule {}
