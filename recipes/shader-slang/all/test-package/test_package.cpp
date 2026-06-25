#include <slang.h>
#include <slang-com-ptr.h>
#include <cassert>
#include <cstdio>

// Create a compile session to see if the thing even works
int main() {
    // Create a global session, the root object of the Slang API
    Slang::ComPtr<slang::IGlobalSession> globalSession;
    SlangResult result = slang::createGlobalSession(globalSession.writeRef());
    assert(SLANG_SUCCEEDED(result));

    // Create a compile session with default options
    slang::SessionDesc sessionDesc = {};
    slang::TargetDesc targetDesc = {};
    targetDesc.format = SLANG_SPIRV;
    targetDesc.profile = globalSession->findProfile("spirv_1_5");
    sessionDesc.targets = &targetDesc;
    sessionDesc.targetCount = 1;

    Slang::ComPtr<slang::ISession> session;
    result = globalSession->createSession(sessionDesc, session.writeRef());
    assert(SLANG_SUCCEEDED(result));

    std::printf("slang session created successfully, package OK\n");
    return 0;
}
