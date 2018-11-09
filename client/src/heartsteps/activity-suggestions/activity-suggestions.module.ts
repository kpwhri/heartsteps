import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { ActivitySuggestionTimeService } from '@heartsteps/activity-suggestions/activity-suggestion-time.service';
import { ActivitySuggestionTimes } from '@heartsteps/activity-suggestions/activity-suggestion-times';
import { IonicPageModule } from 'ionic-angular';

@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule,
        IonicPageModule.forChild(ActivitySuggestionTimes),
    ],
    providers: [
        ActivitySuggestionTimeService
    ],
    declarations: [
        ActivitySuggestionTimes
    ],
    exports: [
        ActivitySuggestionTimes
    ]
})
export class ActivitySuggestionsModule {}
