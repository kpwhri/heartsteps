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

    canActivate():Promise<boolean> {
        return this.authorizationService.isAuthorized()
        .catch(() => {
            this.router.navigate(['welcome']);
            return false;
        })
        .then(() => {
            return this.profileService.isComplete()
        })
        .then(() => {
            this.router.navigate(['/']);
            return false;
        })
        .catch(() => {
            return true;
        });
    }

}
