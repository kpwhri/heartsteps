import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { ActivitySuggestionTimeService } from '@heartsteps/activity-suggestions/activity-suggestion-time.service';
import { ActivitySuggestionTimesComponent } from './activity-suggestion-times';
import { IonicPageModule } from 'ionic-angular';

@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule,
        IonicPageModule.forChild(ActivitySuggestionTimesComponent),
    ],
    providers: [
        ActivitySuggestionTimeService
    ],
    declarations: [
        ActivitySuggestionTimesComponent
    ],
    exports: [
        ActivitySuggestionTimesComponent
    ]
})
export class ActivitySuggestionsModule {}
