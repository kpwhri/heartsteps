import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { WalkingSuggestionTimesComponent } from './walking-suggestion-times.component';
import { IonicPageModule } from 'ionic-angular';
import { WalkingSuggestionTimeService } from './walking-suggestion-time.service';

@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule,
        IonicPageModule.forChild(WalkingSuggestionTimesComponent),
    ],
    providers: [
        WalkingSuggestionTimeService
    ],
    declarations: [
        WalkingSuggestionTimesComponent
    ],
    exports: [
        WalkingSuggestionTimesComponent
    ]
})
export class WalkingSuggestionsModule {}
