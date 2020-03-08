import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { ActivitySurveyService } from './activity-survey.service';

@NgModule({
    imports: [
        InfrastructureModule
    ],
    providers: [
        ActivitySurveyService
    ]
})
export class ActivitySurveysModule {}
