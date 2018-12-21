import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { WalkingSuggestionTimesComponent } from './walking-suggestion-times.component';
import { IonicPageModule } from 'ionic-angular';
import { WalkingSuggestionTimeService } from './walking-suggestion-time.service';
import { WalkingSuggestionService } from './walking-suggestion.service';

@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule,
        IonicPageModule.forChild(WalkingSuggestionTimesComponent),
    ],
    providers: [
        WalkingSuggestionTimeService,
        WalkingSuggestionService
    ],
    declarations: [
        WalkingSuggestionTimesComponent
    ],
    exports: [
        WalkingSuggestionTimesComponent
    ]
})
export class WalkingSuggestionsModule {}
