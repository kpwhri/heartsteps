import { NgModule } from '@angular/core';

import { HeartstepsNotifications } from './heartsteps-notifications.service';
import { InfrastructureModule } from '../infrastructure/infrastructure.module';
import { ParticipantService } from './participant.service';
import { ActivitySuggestionTimeService } from './activity-suggestion-time.service';
import { ActivityPlanService } from '@heartsteps/activity-plan.service';
import { PlacesService } from '@heartsteps/places.service';
import { ContactInformationService } from '@heartsteps/contact-information.service';
import { DateFactory } from "@heartsteps/date.factory";
import { ReflectionTimeService } from '@heartsteps/reflection-time.service';


@NgModule({
    imports: [
        InfrastructureModule
    ],
    providers: [
        ContactInformationService,
        HeartstepsNotifications,
        ParticipantService,
        ActivitySuggestionTimeService,
        ActivityPlanService,
        PlacesService,
        DateFactory,
        ReflectionTimeService
    ]
})
export class HeartstepsModule {}
