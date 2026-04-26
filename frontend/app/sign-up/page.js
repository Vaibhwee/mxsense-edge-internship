import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";


export default async function SignUpPage({ searchParams }) {
  const cookieStore = await cookies();
  const hasSession = cookieStore.get("mxsense_session")?.value === "active";

  if (hasSession) {
    redirect("/dashboard");
  }

  const params = await Promise.resolve(searchParams);
  const errorParam = params?.error;
  let errorMessage = "";
  if (typeof errorParam === "string" && errorParam.trim()) {
    try {
      errorMessage = decodeURIComponent(errorParam);
    } catch {
      errorMessage = errorParam;
    }
  }

  return (
    <main>
      <div className="login-screen">
        <div className="login-card">
          <div className="login-copy">
            <h1>Create account</h1>
            <p>Set up your MXSense workspace access.</p>
          </div>

          {errorMessage ? (
            <p className="login-error" role="alert">
              {errorMessage}
            </p>
          ) : null}

          <form action="/auth/sign-up" className="login-form" method="post">
            <div className="login-field">
              <span>FULL NAME</span>
              <input autoComplete="name" name="full_name" type="text" />
            </div>

            <div className="login-field">
              <span>EMAIL</span>
              <input autoComplete="email" name="email" type="email" />
            </div>

            <div className="login-field">
              <span>USERNAME</span>
              <input autoComplete="username" name="username" type="text" />
            </div>

            <div className="login-field">
              <span>PASSWORD</span>
              <input autoComplete="new-password" name="password" type="password" />
            </div>

            <button className="ui-button ui-button-rect login-button" type="submit">
              Create account
            </button>
          </form>

          <div className="login-footer">
            Already have an account? <Link href="/">Sign in</Link>
          </div>
        </div>
      </div>
    </main>
  );
}
