package com.example.repository;

import com.example.entity.Trade;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TradeRepository extends JpaRepository<Trade, Long> {
    List<Trade> findByModelIdOrderByTimestampDesc(Long modelId);
    
    List<Trade> findByModelIdAndCoinOrderByTimestampDesc(Long modelId, String coin);
    
    @Modifying
    @Query("DELETE FROM Trade t WHERE t.modelId = :modelId")
    void deleteByModelId(@Param("modelId") Long modelId);
}