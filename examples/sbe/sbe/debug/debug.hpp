#ifndef SBE_UT_DEBUG_HPP_INLUCDED
#define SBE_UT_DEBUG_HPP_INLUCDED

#ifdef _lint
    #include <stdlib.h>
    #define SBE_LINT_ASSERT( expr )         ((expr) ? (void)0 : exit(1))
#else
    #define SBE_LINT_ASSERT( expr )         static_cast<void>(0)
#endif

#ifdef SBE_DEBUG
    #ifdef _lint
        #define SBE_ASSERT( expr )      SBE_LINT_ASSERT( expr )
    #else
        #include <assert.h>
        #define SBE_ASSERT( expr )      assert( expr )
    #endif
#else
    #define SBE_ASSERT( expr )          static_cast<void>(0)
#endif


namespace sbe
{
    template<bool> struct StaticAssertHelper;
    template<> struct StaticAssertHelper<true> {};
}

#define SBE_STATIC_ASSERT(expr, msg)    { sbe::StaticAssertHelper<!!(expr)>  static_assert_##__LINE__##msg; static_cast<void>(static_assert_##__LINE__##msg); }


#endif  // #ifndef SBE_UT_DEBUG_HPP_INLUCDED


