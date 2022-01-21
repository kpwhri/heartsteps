import { Injectable } from "@angular/core";
import { CanActivate, Router } from "@angular/router";
import { ProfileService } from "@heartsteps/participants/profile.factory";
import { AuthorizationService } from "@infrastructure/authorization.service";

@Injectable()
export class OnboardGaurd implements CanActivate {

    constructor(
        private authorizationService: AuthorizationService,
        private profileService: ProfileService,
        private router: Router
    ){}

    canActivate(): Promise<boolean> {
        console.log("OnboardGaurd.canActivate() case 1");
        return this.authorizationService.isAuthorized()
            .catch(() => {
                console.log("OnboardGaurd.canActivate() case 2");
                this.router.navigate(['welcome']);
                console.log("OnboardGaurd.canActivate() case 3");
            return false;
        })
            .then(() => {
                console.log("OnboardGaurd.canActivate() case 4");
            return this.profileService.isComplete()
        })
            .then(() => {
                console.log("OnboardGaurd.canActivate() case 5");
                this.router.navigate(['/']);
                console.log("OnboardGaurd.canActivate() case 6");
            return false;
        })
            .catch((error) => {
                console.log("OnboardGaurd.canActivate() case 7", error);
            return true;
        });
    }

}
