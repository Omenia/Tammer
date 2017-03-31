import jenkins.model.*
import hudson.security.*
import org.jenkinsci.plugins.googlelogin.GoogleOAuth2SecurityRealm

def instance = Jenkins.getInstance()

def googleRealm = new GoogleOAuth2SecurityRealm('{{ google_clientid }}', '{{ google_secret }}', '{{ google_auth_domain }}')
instance.setSecurityRealm(googleRealm)

def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
instance.setAuthorizationStrategy(strategy)
instance.save()
