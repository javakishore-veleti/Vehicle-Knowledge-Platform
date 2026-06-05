import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { switchMap } from 'rxjs/operators';
import { AuthService } from './auth.service';

/**
 * Attaches the admin bearer token to /admin/** API calls (enforced by vkp-jwt-rbac). Other paths
 * — including the /customer/user signin itself and /guardrails — pass through untouched, so there
 * is no signin loop.
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  if (!req.url.startsWith('/admin/')) {
    return next(req);
  }
  const auth = inject(AuthService);
  return auth.ensureToken().pipe(
    switchMap(token => next(token
      ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
      : req))
  );
};
