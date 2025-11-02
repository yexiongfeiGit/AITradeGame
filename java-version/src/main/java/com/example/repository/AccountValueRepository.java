package com.example.repository;

import com.example.entity.AccountValue;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AccountValueRepository extends JpaRepository<AccountValue, Long> {
    List<AccountValue> findByModelIdOrderByTimestampDesc(Long modelId);
    
    List<AccountValue> findByModelIdOrderByTimestampDesc(Long modelId, org.springframework.data.domain.Pageable pageable);
    
    @Modifying
    @Query("DELETE FROM AccountValue a WHERE a.modelId = :modelId")
    void deleteByModelId(@Param("modelId") Long modelId);
}