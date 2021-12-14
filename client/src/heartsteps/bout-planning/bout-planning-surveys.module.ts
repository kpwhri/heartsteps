import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { BoutPlanningSurveyService } from './bout-planning-survey.service';

@NgModule({
    imports: [
        InfrastructureModule
    ],
    providers: [
        BoutPlanningSurveyService
    ]
})
export class BoutPlanningSurveysModule {}
