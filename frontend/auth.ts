import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
import jwt from "jsonwebtoken";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [Google],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.apiToken = jwt.sign(
          { sub: user.email },
          process.env.AUTH_SECRET!,
          { expiresIn: "7d" }
        );
      }
      return token;
    },
    async session({ session, token }) {
      (session as any).apiToken = token.apiToken;
      return session;
    },
  },
});
