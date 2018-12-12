import { Injectable } from "@angular/core";
import { CanActivate, Router } from "@angular/router";
import { ProfileService } from "@heartsteps/participants/profile.factory";
import { AuthorizationService } from "@infrastructure/authorization.service";

@Injectable()
export class AuthorizationGaurd implements CanActivate {

    constructor(
        private authorizationService: AuthorizationService,
        private router: Router
    ){}

    canActivate():Promise<boolean> {
        return this.authorizationService.isAuthorized()
        .then(() => {
            return true;
        })
        .catch(() => {
            this.router.navigate(['welcome']);
            return false;
        });
    }
}

@Injectable()
export class OnboardGaurd implements CanActivate {

    constructor(
        private profileService: ProfileService,
        private router: Router
    ){}

    canActivate():Promise<boolean> {
        return this.profileService.isComplete()
        .then(() => {
            return true;
        })
        .catch(() => {
            this.router.navigate(['onboard']);
            return false;
        });
    }

}
