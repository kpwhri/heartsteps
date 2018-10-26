import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { NotificationsModule } from '@heartsteps/notifications/notifications.module';

import { ParticipantService } from './participant.service';
import { PlacesService } from '@heartsteps/places.service';
import { ContactInformationService } from '@heartsteps/contact-information.service';
import { DateFactory } from "@heartsteps/date.factory";
import { ReflectionTimeService } from '@heartsteps/reflection-time.service';
import { ProfileService } from '@heartsteps/profile.factory';
import { FitbitService } from '@heartsteps/fitbit.service';
import { LocationService } from '@heartsteps/location.service';
import { ActivityModule } from '@heartsteps/activity/activity.module';
import { ActivitySuggestionsModule } from '@heartsteps/activity-suggestions/activity-suggestions.module';


@NgModule({
    imports: [
        InfrastructureModule,
        NotificationsModule,
        ActivityModule,
        ActivitySuggestionsModule
    ],
    providers: [
        ContactInformationService,
        ParticipantService,
        ProfileService,
        PlacesService,
        DateFactory,
        ReflectionTimeService,
        FitbitService,
        LocationService
    ]
})
export class HeartstepsModule {}
