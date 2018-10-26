import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { ActivitySuggestionTimeService } from '@heartsteps/activity-suggestions/activity-suggestion-time.service';

@NgModule({
    imports: [
        InfrastructureModule
    ],
    providers: [
        ActivitySuggestionTimeService
    ]
})
export class ActivitySuggestionsModule {}
