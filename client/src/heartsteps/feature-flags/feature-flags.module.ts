import { NgModule } from "@angular/core";

import { InfrastructureModule } from "@infrastructure/infrastructure.module";
import { FeatureFlagService } from "./feature-flags.service";

@NgModule({
    imports: [InfrastructureModule],
    providers: [FeatureFlagService],
})
export class FeatureFlagModule {}
