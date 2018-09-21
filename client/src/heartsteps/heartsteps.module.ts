import { NgModule } from '@angular/core';

import { NotificationService } from './notification.service';
import { InfrastructureModule } from '../infrastructure/infrastructure.module';
import { ParticipantService } from './participant.service';
import { ActivitySuggestionTimeService } from './activity-suggestion-time.service';
import { ActivityPlanService } from '@heartsteps/activity-plan.service';
import { PlacesService } from '@heartsteps/places.service';
import { ContactInformationService } from '@heartsteps/contact-information.service';
import { DateFactory } from "@heartsteps/date.factory";
import { ReflectionTimeService } from '@heartsteps/reflection-time.service';
import { ActivityLogService } from '@heartsteps/activity-log.service';
import { ProfileService } from '@heartsteps/profile.factory';
import { FitbitService } from '@heartsteps/fitbit.service';


@NgModule({
    imports: [
        InfrastructureModule
    ],
    providers: [
        ContactInformationService,
        NotificationService,
        ParticipantService,
        ProfileService,
        ActivitySuggestionTimeService,
        ActivityPlanService,
        ActivityLogService,
        PlacesService,
        DateFactory,
        ReflectionTimeService,
        ActivityLogService,
        FitbitService
    ]
})
export class HeartstepsModule {}
