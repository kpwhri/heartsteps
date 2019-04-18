import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { WalkingSuggestionTimesComponent } from './walking-suggestion-times.component';
import { IonicPageModule } from 'ionic-angular';
import { WalkingSuggestionTimeService } from './walking-suggestion-time.service';
import { WalkingSuggestionService } from './walking-suggestion.service';
import { FormModule } from '@infrastructure/form/form.module';
import { ReactiveFormsModule } from '@angular/forms';

@NgModule({
    imports: [
        InfrastructureModule,
        FormModule,
        ReactiveFormsModule,
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
