// BSD 3-Clause License; see https://github.com/scikit-hep/awkward-1.0/blob/main/LICENSE

#ifndef AWKWARD_GROWABLEBUFFER_H_
#define AWKWARD_GROWABLEBUFFER_H_

#include "awkward/common.h"
#include "awkward/builder/ArrayBuilderOptions.h"
#include "awkward/kernel-dispatch.h"

#include <memory>

namespace awkward {
  /// @class GrowableBuffer
  ///
  /// @brief Contiguous, one-dimensional array that can grow indefinitely
  /// by calling #append.
  ///
  /// Configured by ArrayBuilderOptions, the buffer starts by reserving
  /// {@link ArrayBuilderOptions#initial ArrayBuilderOptions::initial} slots.
  /// When the number of slots used reaches the number reserved, a new
  /// panel is allocated that has slots equal to reserved.
  ///
  /// When {@link ArrayBuilder#snapshot ArrayBuilder::snapshot} is called,
  /// these panels are copied and concatenated to the new Content array.
  template <typename T>
  class LIBAWKWARD_EXPORT_SYMBOL GrowableBuffer {
    using UniquePtrDeleter = decltype(kernel::array_deleter<T>());
    using UniquePtr = std::unique_ptr<T, UniquePtrDeleter>;

    struct GrowableBufferPanel {
      /// @brief Creates a GrowableBufferPanel by allocating a new Panel,
      /// taking an initial #reserved from
      /// {@link ArrayBuilderOptions#initial ArrayBuilderOptions::initial}.
      GrowableBufferPanel(size_t reserved);

      /// @brief Deletes a Panel.
      ~GrowableBufferPanel();

      size_t length;
      std::unique_ptr<GrowableBufferPanel> next;
      UniquePtr ptr;
    };

  public:
    /// @brief Creates an empty GrowableBuffer.
    ///
    /// @param options Configuration options for building an array.
    static GrowableBuffer<T>
      empty(const ArrayBuilderOptions& options);

    /// @brief Creates an empty GrowableBuffer with a minimum reservation.
    ///
    /// @param options Configuration options for building an array.
    /// @param minreserve The initial reservation will be the maximum
    /// of `minreserve` and
    /// {@link ArrayBuilderOptions#initial ArrayBuilderOptions::initial}.
    static GrowableBuffer<T>
      empty(const ArrayBuilderOptions& options, size_t minreserve);

    /// @brief Creates a GrowableBuffer in which all elements are initialized
    /// to a given value.
    ///
    /// @param options Configuration options for building an array.
    /// @param value The initialization value.
    /// @param length The number of elements to initialize (and the
    /// GrowableBuffer's initial #length).
    ///
    /// This is similar to NumPy's
    /// [full](https://docs.scipy.org/doc/numpy/reference/generated/numpy.full.html).
    static GrowableBuffer<T>
      full(const ArrayBuilderOptions& options, T value, size_t length);

    /// @brief Creates a GrowableBuffer in which the elements are initialized
    /// to numbers counting from `0` to `length`.
    ///
    /// @param options Configuration options for building an array.
    /// @param length The number of elements to initialize (and the
    /// GrowableBuffer's initial #length).
    ///
    /// This is similar to NumPy's
    /// [arange](https://docs.scipy.org/doc/numpy/reference/generated/numpy.arange.html).
    static GrowableBuffer<T>
      arange(const ArrayBuilderOptions& options, size_t length);

    /// @brief Creates a GrowableBuffer from a full set of parameters.
    ///
    /// @param options Configuration options for building an array.
    /// @param ptr Reference-counted pointer to the array buffer.
    /// @param length Currently used number of elements.
    /// @param reserved Currently allocated number of elements.
    /// @param head Pointer to the first panel.
    /// @param tail Pointer to the last panel.
    /// @param panels Currently used number of panels.
    ///
    /// Although the #length increments every time #append is called,
    /// it is always less than or equal to #reserved because of reallocations.
    GrowableBuffer(const ArrayBuilderOptions& options,
                   UniquePtr ptr,
                   size_t length,
                   size_t reserved,
                   GrowableBufferPanel *head,
                   GrowableBufferPanel *tail,
                   size_t panels
                   );

    /// @brief Creates a GrowableBuffer by allocating a new buffer, taking an
    /// initial #reserved from
    /// {@link ArrayBuilderOptions#initial ArrayBuilderOptions::initial}.
    GrowableBuffer(const ArrayBuilderOptions& options);

    /// @brief Reference to a unique pointer to the array buffer.
    const GrowableBuffer::UniquePtr&
      ptr();

    /// @brief FIXME: needed for uproot.cpp - remove when it's gone.
    /// Note, it transfers ownership of the array buffer.
    GrowableBuffer::UniquePtr
      get_ptr();

    /// @brief Currently used number of elements.
    ///
    /// Although the #length increments every time #append is called,
    /// it is always less than or equal to #reserved because of reallocations.
    size_t
      length() const;

    /// @brief Changes the #length in-place and possibly reallocate.
    ///
    /// If the `newlength` is larger than #reserved, #ptr is reallocated.
    void
      set_length(size_t newlength);

    /// @brief Currently allocated number of elements.
    ///
    /// Although the #length increments every time #append is called,
    /// it is always less than or equal to #reserved because of reallocations.
    size_t
      reserved() const;

    /// @brief Possibly changes the #reserved and reallocate.
    ///
    /// The parameter only guarantees that at least `minreserved` is reserved;
    /// if an amount less than #reserved is requested, nothing changes.
    ///
    /// If #reserved actually changes, #ptr is reallocated.
    void
      set_reserved(size_t minreserved);

    /// @brief Currently used number of panels.
    size_t
      panels() const;

    /// @brief Inserts one `datum` into the array in panel.
    void
      fill_panel(T datum, size_t reserved);

    /// @brief Creates a new panel with slots equal to #reserved
    void
      add_panel(size_t reserved);

    /// @brief Discards accumulated data, the #reserved returns to
    /// {@link ArrayBuilderOptions#initial ArrayBuilderOptions::initial},
    /// and a new #ptr is allocated.
    void
      clear();

    /// @brief Inserts one `datum` into the array, possibly triggering a
    /// reallocation.
    ///
    /// This increases the #length by 1; if the new #length is larger than
    /// #reserved, a new panel will be allocated.
    void
      append(T datum);

    /// @brief Returns the element at a given position in the array, without
    /// handling negative indexing or bounds-checking.
    T
      getitem_at_nowrap(int64_t at) const;

    /// @brief Compacts all accumulated data from multiple panels to one
    /// contiguously allocated memory panel
    void
      concatenate() ;

  private:
    const ArrayBuilderOptions options_;
    // @brief See #ptr.
    UniquePtr ptr_;
    // @brief See #length.
    size_t length_;
    // @brief See #reserved.
    size_t reserved_;
    GrowableBufferPanel *head_;
    GrowableBufferPanel *tail_;
    size_t panels_;
  };
}

#endif // AWKWARD_GROWABLEBUFFER_H_
